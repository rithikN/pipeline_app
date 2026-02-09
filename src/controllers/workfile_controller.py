# controllers/work_files_controller.py

import json
import os, sys
import subprocess
import tempfile
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple, Any, Optional

import logging, platform
import re
from datetime import datetime

from controllers.base_controller import BaseController
from pipeline.events import Event
from services.data_service import create_file, version_up_file, check_ftp_connection, finalize_file_record
from pipeline.infra.rclone import copy_through_rclone
from services.constants import (
    CREATE_FILE_TASK_SLUG ,CREATE_FILE_USER_SLUG, CREATE_FILE_PLATFORM_KEY, CREATE_FILE_PLATFORM_HOME,
    TASK_SLUG, TASK_ASSIGNED, TASK_EMPLOYEE, TASK_EMPLOYEE_SLUG
)


logger = logging.getLogger(__name__)



# Accept:
#   asset -> SHOW:asset:CHR:BTL:mdl
#   shot  -> SHOW:shot:SQ010:SH010:lay           (legacy)
#   shot  -> SHOW:shot:EP101:SQ010:SH010:lay     (new)

_PIPELINE_UID_RE = re.compile(
    r"^[A-Za-z0-9]+:(?:"
    r"asset:[^:]+:[^:]+:[^:]+"
    r"|shot:(?:EP\d+:)?SQ\d+:SH\d+:[^:]+"
    r")$",
    re.IGNORECASE,
)

_EP_RE = re.compile(r"\b(EP\d+)\b", re.IGNORECASE)
_SQ_RE = re.compile(r"\b(SQ\d+)\b", re.IGNORECASE)
_SH_RE = re.compile(r"\b(SH\d+)\b", re.IGNORECASE)
_ASSET_STEM_RE = re.compile(r"^(?:(?P<show>[A-Z0-9]+)_)?(?P<kind>CHR|PRP|ENV|SET)_(?P<name>[A-Z0-9]+)_", re.I)

# ToDo temp solution
def _infer_ns_from_asset_path(show_code: str, path_str: str) -> str:
    """
    Infer namespace 'CAT' from:
      HLD_CHR_CAT_LDV_V001.ma  -> CAT
      HLD_PRP_BLK_LDV_V002.ma  -> BLK
    """
    stem = Path(path_str).stem.upper()
    m = _ASSET_STEM_RE.match(stem)
    if not m:
        return ""
    return (m.group("name") or "").upper().strip()

def _normalize_dep_kind_from_path(path_str: str) -> str:
    ext = Path(path_str).suffix.lower()
    if ext == ".abc":
        return "shot_cache"
    # default for maya referencing in LIT is asset_file
    return "asset_file"

def _coalesce_dependency_inputs(task_data: dict) -> list[dict[str, Any]]:
    """
    Canonical dependency list for DCC:
      1) pipeline.dependency_inputs  (preferred; already resolved by backend)
      2) tokens.DEPENDENCY.references
      3) pipeline.references (legacy)

    IMPORTANT:
      - Keep multiple occurrences (same path but different namespace/occurrence_index)
      - Only dedupe exact duplicates (same path + same namespace + same occurrence_index)
      - Do NOT scan filesystem for "latest" here; backend already resolved.
    """
    pipeline = task_data.get("pipeline") or {}
    fc = ((pipeline.get("actions") or {}).get("for_create") or {})
    tokens = fc.get("tokens") or {}
    dep = tokens.get("DEPENDENCY") or {}
    ent = task_data.get("entity") or {}
    show_code = (ent.get("show_code") or "HLD").strip().upper()

    out: list[dict[str, Any]] = []

    # 1) main sources
    for src in (
        pipeline.get("dependency_inputs"),
        dep.get("references"),
        pipeline.get("references"),
    ):
        if isinstance(src, list):
            out.extend([x for x in src if isinstance(x, dict)])

    fixed: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int]] = set()

    for item in out:
        path_str = (item.get("path") or "").strip()
        if not path_str:
            continue

        # Normalize path (keep original Windows path in meta if you want; DCC prefers posix)
        p_norm = Path(path_str).as_posix()
        if not _path_exists(path_str) and _path_exists(p_norm):
            path_str = p_norm

        # If still bad, skip (resolver/unresolved will report it)
        if not _path_exists(path_str):
            # Backend should have resolved; skip if missing
            continue

        meta = item.get("meta") if isinstance(item.get("meta"), dict) else {}
        namespace = (meta.get("namespace") or item.get("namespace") or "").strip()
        occ_idx = meta.get("occurrence_index") or item.get("occurrence_index") or 0
        try:
            occ_idx_i = int(occ_idx)
        except Exception:
            occ_idx_i = 0

        # If backend didn't provide namespace for asset_file, infer (fallback only)
        kind = (item.get("kind") or "").strip() or _normalize_dep_kind_from_path(path_str)
        if kind == "asset_file" and not namespace:
            inferred = _infer_ns_from_asset_path(show_code, path_str)
            namespace = inferred or namespace

        key = (Path(path_str).as_posix().lower(), namespace.lower(), occ_idx_i)
        if key in seen:
            continue
        seen.add(key)

        fixed.append({
            **item,
            "path": Path(path_str).as_posix(),
            "kind": kind,
            "meta": {**meta, "namespace": namespace, "occurrence_index": occ_idx_i},
        })

    return fixed

# --------------------------------------------------------------------------------------
# FILE FINDER
# --------------------------------------------------------------------------------------

@dataclass(frozen=True)
class FileFinderOptions:
    version_regex: str = r"(?:^|[_\.])v(\d{1,4})(?:\D|$)"
    max_files_scanned: int = 5000
    allowed_extensions: Optional[Sequence[str]] = None  # None => allow all


def _iter_candidate_files(root: Path, max_files: int) -> Iterable[Path]:
    scanned = 0
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            yield Path(dirpath) / fn
            scanned += 1
            if scanned >= max_files:
                return


def find_latest_version_file(
    root: Path,
    *,
    patterns: Optional[List[str]] = None,
    opts: Optional[FileFinderOptions] = None,
) -> Optional[Path]:
    opts = opts or FileFinderOptions()
    if not root.exists() or not root.is_dir():
        return None

    allowed_exts = None
    if opts.allowed_extensions:
        allowed_exts = {e.lower() for e in opts.allowed_extensions}

    version_re = re.compile(opts.version_regex, re.IGNORECASE)

    candidates: List[Path] = []
    if patterns:
        for pat in patterns:
            candidates.extend(root.glob(pat))
    else:
        candidates.extend(_iter_candidate_files(root, opts.max_files_scanned))

    best: Optional[Tuple[int, float, Path]] = None  # (version, mtime, path)

    for p in candidates:
        if not p.is_file():
            continue
        if allowed_exts is not None and p.suffix.lower() not in allowed_exts:
            continue

        m = version_re.search(p.name)
        ver = int(m.group(1)) if m else -1
        try:
            mt = p.stat().st_mtime
        except OSError:
            continue

        if best is None or (ver, mt) > (best[0], best[1]):
            best = (ver, mt, p)

    return best[2] if best else None


def _path_exists(p: str) -> bool:
    try:
        return bool(p) and Path(p).exists()
    except Exception:
        return False


# --------------------------------------------------------------------------------------
# UID (unchanged)
# --------------------------------------------------------------------------------------

def _looks_like_pipeline_task_uid(s: str) -> bool:
    return bool(_PIPELINE_UID_RE.match((s or "").strip()))


def _infer_asset_type_name_from_path(show_u: str, workfile_path: str) -> tuple[str, str]:
    """
    Infer (asset_type, asset_name) from:
      - filename: HLD_CHR_BTL_MDL_V001.ma  -> (CHR, BTL)
      - folder  : .../HLD_CHR_BTL/...      -> (CHR, BTL)
    """
    p = Path(workfile_path) if workfile_path else None

    # 1) Try filename stem first
    if p and p.stem:
        tokens = p.stem.split("_")
        # Expect: SHOW_ATYPE_ANAME_TASK_V###
        if len(tokens) >= 4 and tokens[0].upper() == show_u:
            asset_type = tokens[1].upper()

            # If last token looks like V001 then task is -2 and asset_name is tokens[2:-2]
            if tokens[-1].upper().startswith("V") and len(tokens) >= 5:
                asset_name = "_".join(tokens[2:-2]).upper()
            else:
                # fallback: asset_name is everything after type until end
                asset_name = "_".join(tokens[2:]).upper()

            if asset_type and asset_name:
                return asset_type, asset_name

    # 2) Try scanning folder names for "HLD_CHR_BTL"
    if p:
        show_prefix = show_u + "_"
        for part in p.parts:
            up = part.upper()
            if up.startswith(show_prefix) and "_" in up:
                seg = up.split("_")
                if len(seg) >= 3 and seg[0] == show_u:
                    asset_type = seg[1].upper()
                    asset_name = "_".join(seg[2:]).upper()
                    if asset_type and asset_name:
                        return asset_type, asset_name

    raise ValueError(
        f"Cannot infer asset_type/asset_name from workfile_path='{workfile_path}'. "
        f"Expected filename/folder like '{show_u}_CHR_BTL_*' or '{show_u}_PRP_*'."
    )


def build_pipeline_task_uid(
    *,
    show: str,
    dept: str,
    entity_type: str,
    entity_name: str,
    workfile_path: str = "",
    episode: Optional[str] = None,   # <-- add this
) -> str:
    """
    Build deterministic pipeline task uid:
      asset -> HLD:asset:CHR:BTL:mdl
      shot  -> HLD:shot:EP101:SQ010:SH010:lay   (preferred)
              HLD:shot:SQ010:SH010:lay         (legacy fallback)
    """
    show_u = (show or "").strip().upper()
    dept_l = (dept or "").strip().lower()
    etype = (entity_type or "").strip().lower()
    ename = (entity_name or "").strip()

    if not show_u or not dept_l:
        raise ValueError("Cannot build task_uid: show or dept missing")

    if etype == "asset":
        # Prefer full form if provided: HLD_CHR_BTL or CHR_BTL
        parts = ename.split("_") if ename else []
        asset_type = ""
        asset_name = ""

        if len(parts) >= 3 and parts[0].upper() == show_u:
            asset_type = parts[1].upper()
            asset_name = "_".join(parts[2:]).upper()
        elif len(parts) >= 2:
            asset_type = parts[0].upper()
            asset_name = "_".join(parts[1:]).upper()
        else:
            # entity_name is short like "BTL" -> infer from file path
            asset_type, asset_name = _infer_asset_type_name_from_path(show_u, workfile_path)

        uid = f"{show_u}:asset:{asset_type}:{asset_name}:{dept_l}"
        if not _looks_like_pipeline_task_uid(uid):
            raise ValueError(f"Built invalid pipeline task_uid: {uid}")
        return uid

    if etype == "shot":
        # try find SQ/SH in entity_name or file path or filename
        stem = Path(workfile_path).stem if workfile_path else ""
        hay = f"{ename} {workfile_path} {stem}"

        sq = _SQ_RE.search(hay)
        sh = _SH_RE.search(hay)
        if not sq or not sh:
            raise ValueError(f"Cannot derive SQ/SH from entity_name/workfile_path: '{ename}'")

        # Prefer explicit episode param; otherwise infer from name/path/stem
        ep = (episode or "").strip()
        if not ep:
            m_ep = _EP_RE.search(hay)
            ep = m_ep.group(1) if m_ep else ""

        # If we have episode, produce the NEW UID shape
        if ep:
            uid = f"{show_u}:shot:{ep.upper()}:{sq.group(1).upper()}:{sh.group(1).upper()}:{dept_l}"
        else:
            # Legacy fallback (keeps older data working)
            uid = f"{show_u}:shot:{sq.group(1).upper()}:{sh.group(1).upper()}:{dept_l}"

        if not _looks_like_pipeline_task_uid(uid):
            raise ValueError(f"Built invalid pipeline task_uid: {uid}")
        return uid

    raise ValueError(f"Unknown entity_type '{etype}' (expected 'asset' or 'shot')")



# --------------------------------------------------------------------------------------
# DEPENDENCY RESOLUTION
# --------------------------------------------------------------------------------------

def _infer_asset_category_from_search_root(search_root: str) -> str:
    p = Path((search_root or "").replace("\\", "/"))
    parts = [x for x in p.parts if x]
    for i, part in enumerate(parts):
        if part.lower() == "assets" and i + 1 < len(parts):
            return parts[i + 1]
    return "Unknown"


def _category_fallback(task_data: dict, search_root: str, path_str: str) -> str:
    if search_root:
        cat = _infer_asset_category_from_search_root(search_root)
        if cat and cat != "Unknown":
            return cat
    if path_str:
        try:
            cat = _infer_asset_category_from_search_root(str(Path(path_str).parent))
            if cat and cat != "Unknown":
                return cat
        except Exception:
            pass
    ent = task_data.get("entity") or {}
    return (ent.get("asset_category") or "Unknown")


def _collect_reference_candidates(task_data: dict) -> list[dict]:
    """
    Flatten sources so resolve_missing_references_to_latest_files can do one pass.
    IMPORTANT: we keep the raw objects so we can detect dependency_plan vs asset refs.
    """
    pipeline = task_data.get("pipeline") or {}
    tokens = (((pipeline.get("actions") or {}).get("for_create") or {}).get("tokens") or {})
    dep = tokens.get("DEPENDENCY") or {}

    out: list[dict] = []

    # 1) pipeline.references (asset refs)
    for r in (pipeline.get("references") or []):
        meta = (r or {}).get("meta") or {}
        out.append({
            "source": "pipeline.references",
            "path": (r or {}).get("path") or "",
            "search_root": meta.get("search_root") or "",
            "raw": r,
        })

    # 2) tokens.DEPENDENCY.references (asset refs)
    if isinstance(dep, dict):
        for r in (dep.get("references") or []):
            meta = (r or {}).get("meta") or {}
            out.append({
                "source": "tokens.DEPENDENCY.references",
                "path": (r or {}).get("path") or "",
                "search_root": meta.get("search_root") or "",
                "raw": r,
            })

    # 3) pipeline.dependency_plan (shot upstream publish OR asset plan in future)
    for d in (pipeline.get("dependency_plan") or []):
        out.append({
            "source": "pipeline.dependency_plan",
            "path": (d or {}).get("latest_file") or "",
            "search_root": (d or {}).get("search_root") or "",
            "raw": d,
        })

    # 4) tokens.DEPENDENCY.dependency_plan
    if isinstance(dep, dict):
        for d in (dep.get("dependency_plan") or []):
            out.append({
                "source": "tokens.DEPENDENCY.dependency_plan",
                "path": (d or {}).get("latest_file") or "",
                "search_root": (d or {}).get("search_root") or "",
                "raw": d,
            })

    return out


def _looks_like_shot_upstream_publish(raw: dict, search_root: str) -> bool:
    """
    Heuristic for your current shape:
      {"asset": None, "role": "LAY", "search_root": ".../Episodes/.../01_LAY/.../04_Out"}
    """
    if not isinstance(raw, dict):
        return False

    role = raw.get("role") or raw.get("task_code")
    if not role:
        return False

    # # in your current dependency_plan, shot upstream uses asset=None
    # if raw.get("asset", "___MISSING___") is not None:
    #     return False

    # Search root under Episodes is a strong signal it is shot upstream publish.
    # Keep it permissive but safe.
    sr = (search_root or "").replace("\\", "/").lower()
    return "/episodes/" in sr or "\\episodes\\" in (search_root or "").lower()


def _role_from_raw(raw: dict) -> str:
    r = raw.get("role") or raw.get("task_code") or ""
    return str(r).strip().lower()


def resolve_missing_references_to_latest_files(
    task_data: dict
) -> tuple[dict[str, list[str]], dict[str, str], list[dict]]:
    """
    Returns:
      asset_deps_by_category: {"Props": [...], "Characters": [...]}
      upstream_publish_files: {"lay": "C:/.../HLD_EP..._LAY_V002.ma"}
      unresolved: list[dict]
    """
    pipeline = task_data.get("pipeline") or {}
    tokens = (((pipeline.get("actions") or {}).get("for_create") or {}).get("tokens") or {})
    dep = tokens.get("DEPENDENCY") or {}

    # keep unresolved as before
    missing_refs = pipeline.get("missing_references") or []
    if isinstance(dep, dict) and dep.get("missing_references"):
        missing_refs = dep.get("missing_references") or missing_refs

    opts = FileFinderOptions(allowed_extensions=[".ma", ".mb", ".abc"])

    asset_deps_by_category: dict[str, list[str]] = {}
    upstream_publish_files: dict[str, str] = {}
    unresolved: list[dict] = []

    # for de-duping asset deps only
    seen_assets: set[str] = set()

    # ---------- A) Resolve from candidates (refs + dependency_plan) ----------
    for item in _collect_reference_candidates(task_data):
        raw = item.get("raw") or {}
        path_str = (item.get("path") or "").strip()
        search_root = (item.get("search_root") or "").strip()

        if not search_root and path_str:
            try:
                search_root = str(Path(path_str).parent)
            except Exception:
                search_root = ""

        # ALWAYS prefer latest by scanning search_root if we have it
        latest: Optional[Path] = None
        if search_root:
            latest = find_latest_version_file(Path(search_root), patterns=None, opts=opts)

        chosen: Optional[str] = None
        if latest and latest.is_file():
            chosen = latest.as_posix()
        elif path_str and _path_exists(path_str):
            chosen = Path(path_str).as_posix()
        if not chosen:
            unresolved.append({**raw, "_ui_note": f"Could not resolve latest under search_root={search_root}"})
            continue
        # ---- SHOT upstream publish: store by role (eg. lay-> publish.ma) ----
        if _looks_like_shot_upstream_publish(raw, search_root):
            role = _role_from_raw(raw)
            if role:
                upstream_publish_files[role] = chosen  # overwrite => latest wins
                continue
        # ---- otherwise treat as ASSET dependency (existing behavior) ----
        if chosen in seen_assets:
            continue
        seen_assets.add(chosen)

        category = _category_fallback(task_data, search_root, chosen)
        asset_deps_by_category.setdefault(category, []).append(chosen)

    # ---------- B) Resolve missing_refs LAST (optional; keep existing behavior) ----------
    # NOTE: missing_refs here are typically produced by backend; in your ANM example they are for LAY.
    # We try to convert them to upstream_publish_files too if possible (search_root -> latest).
    for item in (missing_refs or []):
        details = (item or {}).get("details") or {}
        search_root = (details.get("search_root") or "").strip()
        if not search_root:
            unresolved.append({**item, "_ui_note": "Missing search_root in missing_references.details"})
            continue

        latest = find_latest_version_file(Path(search_root), patterns=None, opts=opts)
        if not latest:
            unresolved.append({**item, "_ui_note": f"No file found under {search_root}"})
            continue

        chosen = latest.as_posix()

        # if task_code exists, treat it like role for shot upstream
        role = str((item or {}).get("task_code") or "").strip().lower()
        if role:
            upstream_publish_files[role] = chosen
        else:
            # fallback: treat as asset dep (rare)
            if chosen not in seen_assets:
                seen_assets.add(chosen)
                category = _category_fallback(task_data, search_root, chosen)
                asset_deps_by_category.setdefault(category, []).append(chosen)

    return asset_deps_by_category, upstream_publish_files, unresolved


# --------------------------------------------------------------------------------------
# PAYLOAD BUILD (UPDATED)
# --------------------------------------------------------------------------------------

def _build_maya_payload_from_task(task_data: dict) -> dict[str, Any]:
    pipeline = task_data.get("pipeline") or {}
    fc = ((pipeline.get("actions") or {}).get("for_create") or {})
    tokens = fc.get("tokens") or {}
    paths = pipeline.get("paths") or {}
    ent = task_data.get("entity", {}) or {}

    dcc = fc.get("dcc_payload") or {}

    dependency_inputs = _coalesce_dependency_inputs(task_data)

    payload: dict[str, Any] = {
        "show_code": ent.get("show_code") or "HLD",

        "project": (paths.get("basename", "") or "").split("_")[0] or (ent.get("show_code") or "HLD"),
        "entity_type": "asset" if ent.get("kind") == "asset" else "shot",

        "entity_subtype": tokens.get("SUBTYPE"),
        "entity_subtype_code": tokens.get("SUBTYPE_CODE"),
        "entity_name": tokens.get("ENTITY_NAME") or ent.get("name") or "",

        "episode": ent.get("episode"),
        "sequence": ent.get("sequence"),
        "department": tokens.get("DEPARTMENT"),
        "task": task_data.get("name") or "",

        "sub_folders": tokens.get("FOLDERS_TO_CREATE", []),
        "maya_file_path": paths.get("workfile") or "",
        "studio_ocio": tokens.get("STUDIO_OCIO"),

        # canonical list for DCC referencing (supports duplicates)
        "dependency_inputs": dependency_inputs,

        # use backend DCC payload for techspec + camera/audio/template
        "fps": dcc.get("fps"),
        "start": dcc.get("start"),
        "end": dcc.get("end"),
        "handle": dcc.get("handle"),

        "camera_rig": dcc.get("camera_rig"),
        "camera_ns": dcc.get("camera_ns"),

        "audio_root": dcc.get("audio_root"),
        "no_audio": dcc.get("no_audio", False),

        "reference_namespaces": dcc.get("reference_namespaces") or {},
    }

    # pass-through template if backend provided it (LIT etc)
    if dcc.get("master_template_ma"):
        payload["master_template_ma"] = dcc["master_template_ma"]

    return payload


# --------------------------------------------------------------------------------------
# CONTROLLER CLASS
# --------------------------------------------------------------------------------------

class WorkFilesController(BaseController):
    """
    Orchestrates operations related to work files:
    - Create initial v000 file
    - Download file from server
    - Upload file to server (with version up)
    """

    # ToDo strictly temp solution due to deadline,need robust system design.
    #  which should be execution plan
    def _run_mayapy_create_file(
        self,
        *,
        mayapy: str,
        payload: dict[str, Any],
        pythonpath_extra: list[str] | None = None,
    ) -> None:
        # write payload.json to temp
        fd, payload_path = tempfile.mkstemp(suffix=".json", prefix="create_file_")
        os.close(fd)
        with open(payload_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        try:
            env = os.environ.copy()



            existing = env.get("PYTHONPATH", "")

            # Ensure your repo modules are importable by mayapy
            # Add pipeline_app_ui/src (or wherever "pipeline" package lives)
            if pythonpath_extra:
                existing = env.get("PYTHONPATH", "")
                env["PYTHONPATH"] = os.pathsep.join([*pythonpath_extra, existing]) if existing else os.pathsep.join(pythonpath_extra)

            cmd = [
                mayapy,
                "-m",
                "pipeline.steps.file_create.maya_run_core",
                "--payload",
                payload_path,
            ]

            p = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if p.returncode != 0:
                raise RuntimeError(
                    "mayapy create_file failed\n"
                    f"cmd: {' '.join(cmd)}\n"
                    f"stdout:\n{p.stdout}\n"
                    f"stderr:\n{p.stderr}\n"
                )

            # optional: log output
            if p.stdout.strip():
                logger.info("[mayapy stdout]\n%s", p.stdout)
            if p.stderr.strip():
                logger.warning("[mayapy stderr]\n%s", p.stderr)

        finally:
            try:
                os.remove(payload_path)
            except OSError:
                pass


    # --------------------
    # Create File
    # --------------------
    def handle_create_file(self, task_data: dict):
        """
        Handle creation of a new work file for a given task.

        Steps:
          1. Verify FTP connection.
          2. Call backend to create file record.
          3. Prepare folder structure and copy starter file locally.
          4. Emit fileCreated event via the event manager.

        Args:
            task_data (dict): Dictionary with task details.

        Returns:
            dict: Updated task data with work file info.

        Raises:
            RuntimeError: If FTP connection fails or backend call fails.
        """
        with self.operation(
                title="Create File",
                message=f"Creating initial file for: {task_data.get('name')}",
                payload=task_data,
        ):
            # --------------------
            # 1. Connectivity check
            # --------------------
            if not check_ftp_connection(check_FTP_conn=True):
                raise RuntimeError("FTP connection failed")

            # --------------------
            # 2. Call backend
            # --------------------
            import pprint
            pprint.pprint(task_data)
            show = task_data['entity']['show_code']
            task_uid = task_data['id']

            if not show:
                raise RuntimeError("Missing show in task_data (need 'show' or project.code)")
            if not task_uid:
                raise RuntimeError("Missing task_uid in task_data (need 'task_uid' or 'uid')")

            create_out = create_file({
                "show": show,
                "task_uid": task_uid,
                "mode": "create_or_open",  # keep simple; backend already supports this
                "platform_key": platform.system().lower(),
                "platform_home": Path.home().as_posix(),
            })

            request_id = create_out.get("request_id") or ""
            if not request_id:
                raise RuntimeError(f"Backend create_file did not return request_id. response={create_out}")

            # Prefer backend-returned task payload if present; fallback to original
            task_for_create = (
                    create_out.get("task")
                    or create_out.get("data")
                    or create_out
                    or task_data
            )

            # Keep request_id around for logging / later completion
            task_for_create["request_id"] = request_id

            # --------------------
            # 3. Prepare workspace (DCC)
            # --------------------
            ok = False
            err = None
            workfile_path = None
            try:
                action = task_data["pipeline"]["actions"]["for_create"]
                mayapy = action.get("dcc_exec")
                if not mayapy or not Path(mayapy).exists():
                    raise RuntimeError(f"Invalid mayapy executable: {mayapy}")


                # Prefer backend path if provided (source of truth for record)
                workfile_path = create_out.get("workfile_path")
                payload = _build_maya_payload_from_task(task_data)

                if workfile_path:
                    payload["maya_file_path"] = workfile_path  # ToDO ensure DCC writes where backend expects, remove it

                pythonpath_extra = [str(Path(__file__).resolve().parents[3] / "src")]

                self._run_mayapy_create_file(
                    mayapy=mayapy,
                    payload=payload,
                    pythonpath_extra=pythonpath_extra,
                )

                workfile_path = payload["maya_file_path"]
                if not Path(workfile_path).exists():
                    raise RuntimeError(f"Workfile not created: {workfile_path}")

                ok = True

            except Exception as e:
                err = str(e)

                # optional: show UI event immediately
                self.publish_event("fileCreateFailed", Event(
                    title="Create File Failed",
                    message=err,
                    payload={"request_id": request_id, "task_uid": task_uid},
                    type="error",
                ))
                raise

            finally:
                # --------------------
                # finalize backend record (never leave STARTED)
                # --------------------
                try:
                    finalize_file_record({
                        "request_id": request_id,
                        "status": "SUCCESS" if ok else "FAILED",
                        "workfile_path": workfile_path or "",
                        "error": err or "",
                    })
                except Exception:
                    logger.exception("Failed to finalize file record request_id=%s", request_id)

            # --------------------
            # 4. Emit event
            # --------------------
            event = Event(
                title="File Created",
                message=f"Created new work file {workfile_path}",
                payload={"request_id": request_id, "workfile_path": workfile_path, "task_uid": task_uid},
                type="success",
            )
            self.publish_event("fileCreated", event)

            return

    # --------------------
    # Download Work File
    # --------------------
    def handle_download_file(self, file_data: dict):
        with self.operation(
            title="Download File",
            message=f"Downloading {file_data['work_detail']['file_name']}",
            payload=file_data,
        ):
            if not check_ftp_connection(check_FTP_conn=True):
                raise RuntimeError("FTP connection failed")

            server_path = file_data["work_detail"].get("ftp_path")
            local_path = file_data["work_detail"].get("work_file")

            if not server_path or not local_path:
                raise RuntimeError("Invalid file paths for download")

            # Ensure local folder exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            status = copy_through_rclone("copyto", src=server_path, dest=local_path, flags=["--update"])
            if status != 0:
                raise RuntimeError(f"Failed to download {server_path}")

            return local_path

    # --------------------
    # Upload Work File + Version Up
    # --------------------
    def handle_upload_file(self, file_data: dict, task_data: dict):
        with self.operation(
            title="Upload File",
            message=f"Uploading {file_data['work_detail']['file_name']}",
            payload=file_data,
        ):
            if not check_ftp_connection(check_FTP_conn=True):
                raise RuntimeError("FTP connection failed")

            local_path = file_data["work_detail"].get("work_file")
            server_path = file_data["work_detail"].get("ftp_path")

            if not local_path or not server_path:
                raise RuntimeError("Invalid file paths for upload")

            status = copy_through_rclone("copyto", src=local_path, dest=server_path, flags=["--update"])
            if status != 0:
                raise RuntimeError(f"Failed to upload {local_path}")

            # Version up record in backend
            file_path = Path(local_path)
            last_saved = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%d-%m-%Y %I:%M %p")
            file_size = file_path.stat().st_size // (1024 * 1024)

            data_for_backend = {
                "artist_slug": task_data["artist_assigned"]["employee"]["slug"],
                "file_slug": file_data.get("slug"),
                "versions": [{
                    "version_up_file": file_path.as_posix(),
                    "last_saved_time": last_saved,
                    "file_size": file_size,
                }],
                "work_file_path": server_path,
                "file_sync_status": WFA,
            }

            updated_task_data = version_up_file(data_for_backend)
            if not updated_task_data:
                raise RuntimeError("Failed to sync version-up with backend")

            return updated_task_data

    def handle_open_file(self, file_data: dict, task_data: Optional[dict] = None) -> None:
        """
        Open the selected work file through launcher_framework.

        Expected file_data (example):
        {
          'app_name': 'Maya',
          'slug': 'HLD_CHR_CAT_MDL_V001',
          'work_detail': {'file_path': 'C:\\...\\HLD_CHR_CAT_MDL_V001.ma', ...}
        }
        """
        with self.operation(
                title="Open File",
                message=f"Opening {file_data.get('work_detail', {}).get('file_name', '')}",
                payload=file_data,
        ):

            work_detail = file_data.get("work_detail") or {}
            file_path_str = work_detail.get("file_path") or ""
            if not file_path_str:
                raise RuntimeError("Missing work_detail.file_path in file_data")

            file_path = Path(file_path_str)
            if not file_path.exists():
                raise RuntimeError(f"File does not exist: {file_path}")

            applauncher_src = _resolve_applauncher_src()

            # sanity check: module must be here
            if not (applauncher_src / "launcher_framework" / "__main__.py").exists():
                raise RuntimeError(
                    f"launcher_framework not found under: {applauncher_src}\n"
                    f"Set PIPELINE_APPLAUNCHER_SRC to your Applauncher\\src path."
                )

            show = task_data["entity"]["show_code"]
            dept = task_data["task_type"]["code"]
            entity_type = task_data["entity"]["kind"]  # "asset" / "shot"
            entity_name = task_data["entity"]["name"]  # "BTL" (short) or "HLD_CHR_BTL" (full)
            tracker_task_id = str(task_data.get("id") or "")  # UUID from DB/tracker

            pipeline_task_uid = build_pipeline_task_uid(
                show=show,
                dept=dept,
                entity_type=entity_type,
                entity_name=entity_name,
                workfile_path=str(file_path),
                episode=task_data["entity"]["episode"], #ToDo design this properly
            )

            env = os.environ.copy()
            # Make launcher_framework importable
            env["PYTHONPATH"] = str(applauncher_src) + os.pathsep + env.get("PYTHONPATH", "")
            env["PATH"] = str(applauncher_src) + os.pathsep + env.get("PATH", "")

            # IMPORTANT: top-level args must come BEFORE subcommand `run`

            launcher_py = sys.executable  # or env var PIPELINE_LAUNCHER_PYTHON if you have it

            bootstrap = (
                "import sys, runpy;"
                f"sys.path.insert(0, r'{applauncher_src}');"
                "sys.argv = ['launcher_framework'] + sys.argv[1:];"
                "runpy.run_module('launcher_framework', run_name='__main__')"
            )

            cmd = [
                launcher_py,
                "-c", bootstrap,
                "--config-root", str(applauncher_src),
                "run",
                "--show", show,
                "--dept", dept,
                "--file", str(file_path),

                "--token", f"PIPELINE_LAUNCHED_FILE={file_path}",
                "--token", f"PIPELINE_TASK_UID={pipeline_task_uid}",  # pipeline uid (HLD:asset:CHR:BTL:mdl)
                "--token", f"PIPELINE_TASK_ID={tracker_task_id}",  # uuid (optional)
                "--token", f"PIPELINE_ENTITY_TYPE={entity_type}",
                "--token", f"PIPELINE_ENTITY_NAME={entity_name}",
                "--token", f"SHOW={show}",
                "--token", f"DEPT={dept}",
            ]

            if dept:
                cmd += ["--dept", dept]

            logger.info("Launching: %s", " ".join(cmd))

            # Don't block UI — just spawn
            try:
                subprocess.Popen(
                    cmd,
                    env=env,
                    cwd=str(file_path.parent),
                    close_fds=(platform.system() != "Windows"),
                )
            except FileNotFoundError as e:
                raise RuntimeError(
                    "Could not find a Python interpreter to run launcher_framework.\n"
                    "Set PIPELINE_LAUNCHER_PYTHON to a valid python.exe path."
                ) from e

            # # Optional: notify UI
            # self.publish_event("fileOpenStarted", Event(
            #     title="Opening File",
            #     message=f"Opening {file_path.name}",
            #     payload={"show": show, "file_path": str(file_path)},
            #     type="info",
            # ))



def _resolve_applauncher_src() -> Path:
    """
    Path that contains:
      - launcher_framework/
      - config/
      - show_config/
    i.e. .../Applauncher/src
    """
    # 1) Prefer env var (best for studio + packaged exe)
    env_path = os.environ.get("PIPELINE_APPLAUNCHER_SRC", "").strip()

    if env_path:
        p = Path(env_path)
        if p.exists():
            return p

    # 2) Fallback: hardcode your dev path (OK for now)
    return Path(r"C:\Users\sknay\PycharmProjects\cgi\pipeline\Applauncher\src")

