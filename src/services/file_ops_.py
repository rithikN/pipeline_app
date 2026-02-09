"""
file_ops.py
------------
Local filesystem helpers for data_service.
Handles collecting, validating, and versioning work files.

WFH behavior (remote mode):
- Ensure Z: is mapped to the local cache root (subst) (non-fatal).
- Show ONLY workfiles that exist locally on Z:
- If requires_vpn and local list is empty:
    Probe UNC work_dir (best-effort) and set:
      task_data["pipeline"]["wfh_state"]["remote_only_unc"] = True
    so UI can hide/disable Create File (avoid duplicates).
"""
from __future__ import annotations

import os
import re
import logging
import shutil
import time
import fnmatch
from datetime import datetime
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from services.constants import EXCLUDE_MAC_FILES
from pipeline.config.settings import SYSTEM

from pipeline.infra.rclone import copy_through_rclone

logger = logging.getLogger(__name__)

# -----------------------------
# WFH: local-only workfile view
# -----------------------------

ProgressCB = Callable[[str, int, int], None]
_WFH_Z_READY: set[str] = set()
_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
_UDIM_TOKEN_RE = re.compile(r"<\s*(UDIM|UVTILE)\s*>", re.IGNORECASE)
_UDIM_NUM_RE = re.compile(r"(?<!\d)(1\d{3})(?!\d)")


_UDIM_TILE_RE = re.compile(
    r"^(?P<base>.+?)(?P<sep>[._-])(?P<udim>1\d{3})(?P<ext>\.[^.]+)$",
    re.IGNORECASE,
)

def _parse_udim_tile_name(filename: str) -> Optional[Tuple[str, str, int, str]]:
    """
    Returns (base, sep, udim_int, ext) for names like:
      foo.1001.exr
      foo_1001.png
      foo-1001.tif
    """
    name = (filename or "").strip()
    if not name:
        return None
    m = _UDIM_TILE_RE.match(name)
    if not m:
        return None
    return (m.group("base"), m.group("sep"), int(m.group("udim")), m.group("ext"))


def _is_udim_candidate(path_str: str) -> bool:
    """
    True if basename looks like a numbered UDIM tile (1001-1999), e.g. '.1003.png'
    """
    bn = os.path.basename((path_str or "").replace("\\", "/"))
    return _parse_udim_tile_name(bn) is not None


def _copy_udim_set(
    src_one_tile: str,
    dst_one_tile: str,
    *,
    prefer_rclone: bool,
    logger=None,
    check_ftp_connection_fn=None,
) -> Tuple[int, int]:
    """
    Copy ALL UDIM tiles for a set, given a single tile (src/dst).
    Returns: (downloaded_count, skipped_count)

    Works best for UNC/local sources because we can list the directory.
    For rclone-remote schemes, we fall back to copying just the one tile.
    """
    src_n = _norm(src_one_tile)
    dst_n = _norm(dst_one_tile)

    src_bn = os.path.basename(src_n)
    dst_bn = os.path.basename(dst_n)

    s = _parse_udim_tile_name(src_bn)
    if not s:
        # not a UDIM tile; nothing to do
        return (0, 0)

    s_base, s_sep, _s_udim, s_ext = s
    d = _parse_udim_tile_name(dst_bn)
    if d:
        d_base, d_sep, _d_udim, d_ext = d
    else:
        # if dst is weird, mirror src naming
        d_base, d_sep, d_ext = s_base, s_sep, s_ext

    src_dir = os.path.dirname(src_n)
    dst_dir = os.path.dirname(dst_n)

    # If it's a true rclone scheme, we can’t reliably os.listdir().
    if is_remote_scheme(src_dir):
        # Best-effort: copy the one tile only
        if check_ftp_connection_fn and is_remote_scheme(src_n):
            if not check_ftp_connection_fn(check_FTP_conn=True):
                raise RuntimeError("FTP connection failed")

        _copy_idempotent(src_n, dst_n, logger=logger, prefer_rclone=prefer_rclone)
        return (0 if _was_last_copy_skipped() else 1, 1 if _was_last_copy_skipped() else 0)

    # List src_dir and find all matching tiles
    src_dir_os = os.path.normpath(src_dir.replace("/", os.sep))
    try:
        names = os.listdir(src_dir_os)
    except Exception:
        # If listing fails, at least copy the one tile
        _copy_idempotent(src_n, dst_n, logger=logger, prefer_rclone=prefer_rclone)
        return (0 if _was_last_copy_skipped() else 1, 1 if _was_last_copy_skipped() else 0)

    udims: List[int] = []
    for name in names:
        p = _parse_udim_tile_name(name)
        if not p:
            continue
        b, sep, u, ext = p
        if b == s_base and sep == s_sep and ext.lower() == s_ext.lower():
            udims.append(u)

    udims = sorted(set(udims))
    if not udims:
        # should not happen, but safe fallback
        _copy_idempotent(src_n, dst_n, logger=logger, prefer_rclone=prefer_rclone)
        return (0 if _was_last_copy_skipped() else 1, 1 if _was_last_copy_skipped() else 0)

    downloaded = 0
    skipped = 0

    for u in udims:
        src_tile = _norm(f"{src_dir}/{s_base}{s_sep}{u}{s_ext}")
        dst_tile = _norm(f"{dst_dir}/{d_base}{d_sep}{u}{d_ext}")

        try:
            _copy_idempotent(src_tile, dst_tile, logger=logger, prefer_rclone=prefer_rclone)
            if _was_last_copy_skipped():
                skipped += 1
            else:
                downloaded += 1
        except FileNotFoundError:
            # If listing said it exists but copy fails, record as missing
            raise
    return (downloaded, skipped)


def _udim_glob_for_filename(filename: str) -> str:
    """
    Return an rclone/fnmatch-style glob for UDIM sets.
    Examples:
      foo.<UDIM>.exr  -> foo.[0-9][0-9][0-9][0-9].exr
      foo.<UVTILE>.exr-> foo.u*_v*.exr  (common Mari style)
      foo.1001.exr    -> foo.[0-9][0-9][0-9][0-9].exr
    """
    if not filename:
        return ""

    # tokens
    m = _UDIM_TOKEN_RE.search(filename)
    if m:
        token = m.group(1).lower()
        if token == "udim":
            return _UDIM_TOKEN_RE.sub("[0-9][0-9][0-9][0-9]", filename, count=1)
        # UVTILE commonly expands to u1_v1, u2_v1...
        return _UDIM_TOKEN_RE.sub("u*_v*", filename, count=1)

    # numeric (1001 etc)
    if _UDIM_NUM_RE.search(filename):
        return _UDIM_NUM_RE.sub("[0-9][0-9][0-9][0-9]", filename, count=1)

    return ""


def is_remote_scheme(path_str: str) -> bool:
    """
    True only for rclone-style remotes: 'remote:...' / 'ftp:...' / 'sftp:...'
    False for UNC (//server/share), Windows drives (C:\), and normal paths.
    """
    p = (path_str or "").strip()
    if not p:
        return False

    pl = p.lower()

    # UNC
    if pl.startswith("\\\\") or pl.startswith("//"):
        return False

    # Windows drive
    if _DRIVE_RE.match(p):
        return False

    # rclone remote name + ':' (must be >1 to avoid "C:")
    colon = p.find(":")
    return colon > 1


def _is_remote_task(task_data: dict) -> bool:
    env = (task_data or {}).get("pipeline", {}).get("environment", {}) or {}
    return (env.get("mode") or "").strip().lower() == "remote"

def _requires_vpn(task_data: dict) -> bool:
    env = (task_data or {}).get("pipeline", {}).get("environment", {}) or {}
    caps = env.get("capabilities", {}) or {}
    return bool(caps.get("requires_vpn", False))

def _show_code_from_task(task_data: dict) -> str:
    ent = (task_data or {}).get("entity") or {}
    return (ent.get("show_code") or ent.get("show") or "SHOW").strip().upper()

def _ensure_wfh_z_mapped(task_data: dict) -> None:
    """
    Ensure Z: is mapped to the configured local cache root.
    Uses services/wfh_mapping.py (non-fatal).
    Runs once per show per session.
    """
    if not _is_remote_task(task_data):
        return

    show = _show_code_from_task(task_data)
    if show in _WFH_Z_READY:
        return

    # If Z: already usable, don't touch it
    if os.path.exists("Z:/HiddenIsland_Server") or os.path.exists("Z:\\HiddenIsland_Server"):
        _WFH_Z_READY.add(show)
        return

    try:
        from services.wfh_mapping import resolve_local_cache_root, ensure_z_subst
        local_root = resolve_local_cache_root(show)
        ensure_z_subst(local_root)
        _WFH_Z_READY.add(show)
        logger.info("WFH mapping ready: show=%s Z: -> %s", show, local_root)
    except Exception as exc:
        logger.warning("WFH mapping failed (non-fatal): show=%s err=%s", show, exc)


def _map_local_to_remote(local_path: str, path_map: List[dict]) -> str:
    lp = _norm(local_path)
    if not lp:
        return ""

    # already remote (UNC or rclone remote)
    if lp.startswith("//") or is_remote_scheme(lp):
        return lp

    for rule in (path_map or []):
        if not isinstance(rule, dict):
            continue

        src = rule.get("src_prefix") or rule.get("from") or rule.get("local") or ""
        dst = rule.get("dst_prefix") or rule.get("to") or rule.get("remote") or ""
        if not src or not dst:
            continue

        src_n = _norm(str(src))
        if lp.lower().startswith(src_n.lower()):
            return _norm(str(dst).rstrip("/\\")) + lp[len(src_n):]

    return ""


def _extract_file_path(file_item: dict) -> str:
    """
    Robust path extraction:
      - file_item["work_detail"]["file_path"]
      - file_item["work_detail"]["work_file"]
      - file_item["path"]
    """
    if not isinstance(file_item, dict):
        return ""
    wd = file_item.get("work_detail") or {}
    p = wd.get("file_path") or wd.get("work_file") or file_item.get("path") or ""
    return str(p)

def _set_wfh_state(task_data: dict, **kv) -> None:
    """
    Attach transient state for UI decisions.
    """
    try:
        pipe = task_data.setdefault("pipeline", {})
        st = pipe.setdefault("wfh_state", {})
        st.update(kv)
    except Exception:
        pass

def _resolve_unc_root(task_data: dict) -> str:
    """
    UNC base share for probing.
    Prefer env; no hardcoding by default.

    Examples:
      PIPELINE_SERVER_UNC_ROOT=\\10.10.19.52\\HiddenIsland
      HLD_SERVER_UNC_ROOT=\\10.10.19.52\\HiddenIsland
    """
    show = _show_code_from_task(task_data)
    env = os.environ.get("PIPELINE_SERVER_UNC_ROOT") or os.environ.get(f"{show}_SERVER_UNC_ROOT")
    return (env or "").strip()


# ToDo due to deadline, temp solution
def _to_unc_path(local_z_path: str, unc_root: str) -> str:
    """
    Map:
      Z:/HiddenIsland_Server/... -> \\server\share\HiddenIsland_Server\...
    """
    if not local_z_path or not unc_root:
        return ""

    p = local_z_path.replace("\\", "/")

    # Z: root contains HiddenIsland_Server and HiddenIsland_Software (per your subst layout)
    if p.lower().startswith("z:/hiddenisland_server/"):
        rest = p[len("z:/hiddenisland_server/"):]
        return str(Path(unc_root) / "HiddenIsland_Server" / rest)
    if p.lower() == "z:/hiddenisland_server":
        return str(Path(unc_root) / "HiddenIsland_Server")

    if p.lower().startswith("z:/hiddenisland_software/"):
        rest = p[len("z:/hiddenisland_software/"):]
        return str(Path(unc_root) / "HiddenIsland_Software" / rest)
    if p.lower() == "z:/hiddenisland_software":
        return str(Path(unc_root) / "HiddenIsland_Software")

    return ""

def _dir_has_any_files(dir_path: str) -> bool:
    """
    Best-effort: do we see *any* files in this directory?
    """
    if not dir_path:
        return False
    try:
        d = Path(dir_path)
        if not d.exists() or not d.is_dir():
            return False
        for p in d.iterdir():
            if p.is_file():
                return True
    except Exception:
        return False
    return False

def filter_workfiles_for_wfh(task_data: dict, work_files: list[dict]) -> list[dict]:
    """
    Studio:
      - return as-is

    WFH/remote:
      - ensure Z: mapping
      - return ONLY workfiles that exist locally
      - if requires_vpn and local list is empty:
          probe UNC (best-effort) and set task_data["pipeline"]["wfh_state"]["remote_only_unc"]
    """
    if not work_files:
        # Still set state for UI if remote+vpn (local empty)
        if _is_remote_task(task_data) and _requires_vpn(task_data):
            _ensure_wfh_z_mapped(task_data)
            work_dir = (task_data or {}).get("pipeline", {}).get("paths", {}).get("work_dir") or ""
            unc_root = _resolve_unc_root(task_data)
            unc_dir = _to_unc_path(str(work_dir), unc_root)
            unc_has = _dir_has_any_files(unc_dir)
            _set_wfh_state(
                task_data,
                local_empty=True,
                unc_work_dir=unc_dir,
                unc_has_files=unc_has,
                remote_only_unc=bool(unc_has),
            )
        return []

    if not _is_remote_task(task_data):
        return work_files

    _ensure_wfh_z_mapped(task_data)

    visible: list[dict] = []
    for f in work_files:
        p = _extract_file_path(f)
        if not p:
            continue
        try:
            if os.path.exists(p):
                visible.append(f)
        except Exception:
            continue

    # If WFH+VPN and nothing local, probe UNC to avoid showing Create File wrongly
    if _requires_vpn(task_data):
        work_dir = (task_data or {}).get("pipeline", {}).get("paths", {}).get("work_dir") or ""
        unc_root = _resolve_unc_root(task_data)
        unc_dir = _to_unc_path(str(work_dir), unc_root)
        unc_has = _dir_has_any_files(unc_dir) if (not visible) else False
        _set_wfh_state(
            task_data,
            local_empty=(len(visible) == 0),
            unc_work_dir=unc_dir,
            unc_has_files=unc_has,
            remote_only_unc=bool(unc_has),
        )

    return visible


# ----------------------------------------------------------------------
# Latest version helper (your existing)
# ----------------------------------------------------------------------

_VERSION_RE = re.compile(r"(?:^|[_\-\.])v(?P<v>\d+)(?:$|[_\-\.])", re.IGNORECASE)

@dataclass(frozen=True)
class LatestVersionResult:
    is_latest: bool
    current_version: Optional[int]
    latest_version: Optional[int]
    latest_path: Optional[Path]
    version_width: int = 0

def _parse_version(stem: str) -> Optional[Tuple[str, int, int]]:
    matches = list(_VERSION_RE.finditer(stem))
    if not matches:
        return None
    m = matches[-1]
    num_str = m.group("v")
    ver = int(num_str)
    width = len(num_str)
    d_start, d_end = m.start("v"), m.end("v")
    family_key = stem[:d_start] + stem[d_end:]
    return family_key, ver, width

def find_latest_version_on_disk(file_path: str) -> LatestVersionResult:
    try:
        p = Path(file_path)
    except Exception:
        return LatestVersionResult(True, None, None, None)

    if not p.parent.exists():
        return LatestVersionResult(True, None, None, None)

    parsed = _parse_version(p.stem)
    if not parsed:
        return LatestVersionResult(True, None, None, None)

    family_key, cur_ver, width = parsed
    best_ver = cur_ver
    best_path = p

    try:
        for cand in p.parent.iterdir():
            if not cand.is_file():
                continue
            if cand.suffix.lower() != p.suffix.lower():
                continue
            parsed2 = _parse_version(cand.stem)
            if not parsed2:
                continue
            family_key2, ver2, _w2 = parsed2
            if family_key2.lower() != family_key.lower():
                continue
            if ver2 > best_ver:
                best_ver = ver2
                best_path = cand
    except Exception:
        return LatestVersionResult(True, cur_ver, cur_ver, p, width)

    return LatestVersionResult(best_ver == cur_ver, cur_ver, best_ver, best_path, width)


# ----------------------------------------------------------------------
# Workfile listing (USED BY data_service.get_workFiles)
# ----------------------------------------------------------------------

# matches "v001", "_v12_", ".v003.", "-v7-" etc. (already defined above)
# _VERSION_RE = ...

_EXT_TO_APP = {
    ".blend": "Blender",
    ".ma": "Maya",
    ".mb": "Maya",
    ".nk": "Nuke",
    ".hip": "Houdini",
    ".hiplc": "Houdini",
}

# optional: only treat these as "work files"
_ALLOWED_EXTS = set(_EXT_TO_APP.keys())


def _parse_version_token(stem: str) -> str:
    """
    Return 'v002' style token (lowercase) if found; else ''.
    """
    m = _VERSION_RE.search(stem or "")
    if not m:
        return ""
    return f"v{m.group('v').zfill(3)}"


def _guess_app(ext: str, filename: str) -> str:
    # skip blender backups earlier; still safe
    if re.search(r"\.blend\d+$", (filename or "").lower()):
        return "Blender"
    return _EXT_TO_APP.get((ext or "").lower(), "Unknown")


def _slug_for_file(task: dict[str, Any], p: Path) -> str:
    return str(task.get("slug") or p.stem)


def get_work_files(task_data: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Return UI-ready workfile dicts.

    Source folder priority:
      1) task_data["pipeline"]["paths"]["work_dir"]
      2) task_data["work_directory"] (legacy)

    WFH/remote:
      - ensure Z: mapping (best-effort)
      - filter to ONLY existing local paths (Z:)
      - if requires_vpn and local empty:
          probe UNC + set task_data["pipeline"]["wfh_state"]["remote_only_unc"]=True
    """
    # Ensure Z mapping early so Path(work_dir) resolves locally in WFH
    if _is_remote_task(task_data):
        _ensure_wfh_z_mapped(task_data)

    work_dir_path = (
        (task_data or {}).get("pipeline", {}).get("paths", {}).get("work_dir")
        or (task_data or {}).get("work_directory")
        or ""
    )

    work_dir = Path(work_dir_path) if work_dir_path else None
    if not work_dir or not work_dir.exists() or not work_dir.is_dir():
        # important: still allow WFH state to be set (UNC probe) when empty
        return filter_workfiles_for_wfh(task_data, [])

    results: list[dict[str, Any]] = []

    try:
        for p in work_dir.iterdir():
            if not p.is_file():
                continue

            # skip temp/lock files
            if p.name.startswith("~") or p.suffix.lower() in {".tmp", ".lock"}:
                continue

            # exclude mac junk
            if p.name in EXCLUDE_MAC_FILES:
                continue

            # skip blender backups like .blend1/.blend2
            if re.search(r"\.blend\d+$", p.name.lower()):
                continue

            ext = p.suffix.lower()
            if _ALLOWED_EXTS and ext not in _ALLOWED_EXTS:
                continue

            try:
                st = p.stat()
            except OSError:
                continue

            results.append(
                {
                    "app_name": _guess_app(ext, p.name),
                    "version": _parse_version_token(p.stem),  # "v002"
                    "file_size": int((st.st_size + 1023) // 1024),  # KB
                    "date": datetime.fromtimestamp(st.st_mtime).date().isoformat(),
                    "slug": _slug_for_file(task_data, p),
                    "work_detail": {
                        "file_name": p.name,
                        "ext": ext,
                        "file_path": str(p).replace("\\", "/"),
                        "local_path": None,
                        "status": "in_progress",
                    },
                }
            )
    except Exception as exc:
        logger.debug("get_work_files scan failed (non-fatal): %s", exc)

    # Sort: newest version first (numeric), then date
    def _sort_key(d: dict[str, Any]):
        v = (d.get("version") or "").lstrip("v")
        try:
            vnum = int(v) if v else -1
        except Exception:
            vnum = -1
        return (vnum, d.get("date", ""))

    results.sort(key=_sort_key, reverse=True)

    # Apply WFH filter + UNC probe state injection
    return filter_workfiles_for_wfh(task_data, results)


# ----------------------------------------------------------------------
# Backward-compat (data_service imports this)
# ----------------------------------------------------------------------
def sync_local_files(task: dict) -> list[dict]:
    """
    Back-compat helper (kept to avoid import domino issues).
    If you still use server-provided task["work_files"], return it,
    otherwise fall back to scanning local work_dir.
    """
    wf = (task or {}).get("work_files")
    if isinstance(wf, list) and wf:
        return wf
    return get_work_files(task)


@dataclass
class DownloadSummary:
    local_workfile_path: str = ""
    downloaded_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    missing_count: int = 0
    missing: List[Dict[str, Any]] = field(default_factory=list)
    failed: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "local_workfile_path": self.local_workfile_path,
            "downloaded_count": self.downloaded_count,
            "skipped_count": self.skipped_count,
            "failed_count": self.failed_count,
            "missing_count": self.missing_count,
            "missing": self.missing,
            "failed": self.failed,
        }


def download_task_workfile_and_deps(
    task_data: Dict[str, Any],
    file_data: Optional[Dict[str, Any]] = None,
    *,
    progress_cb: Optional[ProgressCB] = None,
    logger=None,
    check_ftp_connection_fn=None,
) -> DownloadSummary:
    summary = DownloadSummary()

    pipeline = (task_data or {}).get("pipeline", {}) or {}
    env = pipeline.get("environment", {}) or {}
    cap = env.get("capabilities", {}) or {}
    mode = (env.get("mode") or "").strip().lower()
    path_map = env.get("path_map") or []

    try:
        _ensure_wfh_z_mapped(task_data)
    except Exception:
        pass

    prefer_rclone = bool(
        cap.get("prefer_rclone", True)
        or cap.get("transport") == "rclone"
        or mode in ("remote", "wfh")
    )

    def _progress(msg: str, cur: int, total: int) -> None:
        if progress_cb:
            progress_cb(msg, cur, total)

    def _maybe_check_ftp(src: str) -> None:
        if check_ftp_connection_fn and is_remote_scheme(src):
            if not check_ftp_connection_fn(check_FTP_conn=True):
                raise RuntimeError("FTP connection failed")

    def _sync_dir(src_dir: str, dst_dir: str) -> None:
        if not src_dir or not dst_dir:
            raise RuntimeError("Empty src/dst for directory sync")

        # If src is remote scheme OR we prefer rclone (UNC copy is fine via rclone copy)
        if is_remote_scheme(src_dir) or prefer_rclone:
            _maybe_check_ftp(src_dir)
            os.makedirs(dst_dir.replace("\\", "/"), exist_ok=True)
            rc = copy_through_rclone(
                rclone_command="copy",
                src=src_dir.replace("\\", "/"),
                dest=dst_dir.replace("\\", "/"),
                flags=_default_rclone_flags(),
            )
            if rc != 0:
                raise RuntimeError(f"rclone dir copy failed rc={rc} for {src_dir} -> {dst_dir}")
            return

        _copy_dir_best_effort(src_dir, dst_dir, retries=3, retry_sleep=0.75, logger=logger)

    def _should_udim_copy(src: str, dst: str) -> bool:
        # Only attempt UDIM copy when it looks like a file target
        if not (src or dst):
            return False
        dst_ext = os.path.splitext((dst or ""))[1]
        src_ext = os.path.splitext((src or ""))[1]
        if not (dst_ext or src_ext):
            return False
        return _is_udim_candidate(src) or _is_udim_candidate(dst)

    def _copy_one(src: str, dst: str, *, meta: Dict[str, Any]) -> None:
        """
        Copy one item, upgrading to UDIM set copy when needed.
        Updates summary counts.
        """
        # Preflight only for true rclone remotes
        if check_ftp_connection_fn and is_remote_scheme(src):
            _maybe_check_ftp(src)

        # UDIM set handling (textures etc.)
        if meta.get("kind") != "workfile" and _should_udim_copy(src, dst):
            try:
                _copy_udim_set(
                    src,
                    dst,
                    prefer_rclone=prefer_rclone,
                    logger=logger,
                    check_ftp_connection_fn=check_ftp_connection_fn,
                )
                # Count as one "downloaded unit" (tiles count unknown for rclone)
                summary.downloaded_count += 1
                return
            except FileNotFoundError:
                summary.missing.append({"reason": "source_not_found", "path": src, "meta": meta, "udim": True})
                summary.missing_count = len(summary.missing)
                return
            except Exception as e:
                summary.failed.append({"error": str(e), "path": src, "meta": meta, "udim": True})
                summary.failed_count += 1
                return

        # Normal path
        try:
            _copy_idempotent(src, dst, logger=logger, prefer_rclone=prefer_rclone)
            if _was_last_copy_skipped():
                summary.skipped_count += 1
            else:
                summary.downloaded_count += 1
        except FileNotFoundError:
            summary.missing.append({"reason": "source_not_found", "path": src, "meta": meta})
            summary.missing_count = len(summary.missing)
        except Exception as e:
            summary.failed.append({"error": str(e), "path": src, "meta": meta})
            summary.failed_count += 1

    # ----------------------------
    # dependency sources
    # ----------------------------
    dep_token = (
        pipeline.get("actions", {})
        .get("for_create", {})
        .get("tokens", {})
        .get("DEPENDENCY", {})
    ) or {}

    if isinstance(pipeline.get("dependency_inputs"), list) and pipeline.get("dependency_inputs"):
        references = pipeline.get("dependency_inputs") or []
    else:
        references = dep_token.get("references") or pipeline.get("references") or []

    missing_refs = (
        dep_token.get("missing_references")
        or dep_token.get("missing")
        or pipeline.get("missing_dependencies")
        or pipeline.get("missing_references")
        or []
    )

    # ----------------------------
    # targets
    # ----------------------------
    paths = pipeline.get("paths") or {}
    local_work_dir = _norm(paths.get("work_dir") or "")
    if not local_work_dir:
        raise RuntimeError("pipeline.paths.work_dir missing (needed for sync).")

    local_workfile = _norm((paths.get("workfile") or paths.get("out_workfile") or "").strip())

    if file_data:
        wd = file_data.get("work_detail") or {}
        local_override = wd.get("work_file") or wd.get("file_path")
        if local_override:
            local_workfile = _norm(str(local_override))

    # Decide mode
    force_fallback = (file_data is None)  # task-list download wants all versions
    no_refs = (not isinstance(references, list)) or (len(references) == 0)
    use_fallback = bool(force_fallback or no_refs)

    # ----------------------------
    # Fallback: sync all versions + BFS
    # ----------------------------
    if use_fallback:
        remote_work_dir = _map_local_to_remote(local_work_dir, path_map)
        if not remote_work_dir:
            raise RuntimeError(f"Failed to derive remote work_dir from local via path_map: {local_work_dir}")

        _progress("Syncing work_dir (all versions)...", 0, 1)
        _sync_dir(remote_work_dir, local_work_dir)

        entry = _latest_maya_in_work_dir(local_work_dir) or local_workfile
        entry = _norm(entry)
        if not entry or not Path(entry).exists():
            raise RuntimeError("No Maya workfile found locally after syncing work_dir.")

        summary.local_workfile_path = entry

        # Optional extras (now UDIM-aware too, harmless)
        dcc = (pipeline.get("actions", {}).get("for_create", {}).get("dcc_payload", {}) or {})
        for extra in (dcc.get("camera_rig"), dcc.get("studio_ocio")):
            if not extra:
                continue
            try:
                src_r, dst_l = _resolve_dep_src_dst(
                    str(extra),
                    base_dir=str(Path(entry).parent),
                    path_map=path_map,
                )
                if src_r and dst_l:
                    _copy_one(src_r, dst_l, meta={"kind": "extra", "extra": str(extra)})
            except Exception:
                pass

        mayapy = (pipeline.get("actions", {}).get("for_create", {}).get("dcc_exec") or "").strip()
        if not mayapy:
            summary.missing.append({"reason": "mayapy_missing_for_bfs", "path": entry})
            summary.missing_count = len(summary.missing)
            return summary

        # BFS recursion (UDIM handled inside _download_maya_deps_bfs you already updated)
        try:
            _download_maya_deps_bfs(
                entry_local_maya=entry,
                task_data=task_data,
                path_map=path_map,
                mayapy=mayapy,
                summary=summary,
                progress_cb=progress_cb,
                logger=logger,
                prefer_rclone=prefer_rclone,
                check_ftp_connection_fn=check_ftp_connection_fn,
            )
        except Exception as e:
            summary.failed.append({"error": str(e), "path": entry})
            summary.failed_count += 1

        # carry backend missing
        for m in (missing_refs or []):
            summary.missing.append({"reason": "backend_missing", "ref": m})
        summary.missing_count = len(summary.missing)
        return summary

    # ----------------------------
    # Token-driven: workfile + refs
    # ----------------------------
    if not local_workfile:
        raise RuntimeError("No local workfile target found (pipeline.paths.workfile missing).")

    summary.local_workfile_path = local_workfile

    remote_workfile = _map_local_to_remote(local_workfile, path_map)
    if not remote_workfile:
        raise RuntimeError(f"Failed to derive remote source from local workfile using path_map: {local_workfile}")

    items: List[Tuple[str, str, Dict[str, Any]]] = [(remote_workfile, local_workfile, {"kind": "workfile"})]

    for ref in (references or []):
        if not isinstance(ref, dict):
            continue
        src_or_local = _extract_reference_path(ref)
        if not src_or_local:
            continue
        src_or_local = _norm(src_or_local)

        if src_or_local.lower().startswith("z:/") or _DRIVE_RE.match(src_or_local):
            dst_local = src_or_local
            src_remote = _map_local_to_remote(dst_local, path_map)
        else:
            src_remote = src_or_local
            dst_local = _map_remote_to_local(src_remote, path_map)

        if not src_remote or not dst_local:
            summary.missing.append({"reason": "unmappable", "ref": ref, "path": src_or_local})
            continue

        items.append((src_remote, dst_local, {"kind": ref.get("kind") or "dependency", "ref": ref}))

    for m in (missing_refs or []):
        summary.missing.append({"reason": "backend_missing", "ref": m})
    summary.missing_count = len(summary.missing)

    total = len(items)
    for i, (src, dst, meta) in enumerate(items, start=1):
        msg = (
            "Downloading workfile..."
            if meta.get("kind") == "workfile"
            else f"Downloading dependencies ({i-1}/{max(total-1, 1)})..."
        )
        _progress(msg, i, total)

        # UDIM-aware copy path
        _copy_one(src, dst, meta=meta)

    return summary


# ----------------------------
# Helpers (mapping + copy)
# ----------------------------

_LAST_COPY_SKIPPED = False

def _was_last_copy_skipped() -> bool:
    return bool(_LAST_COPY_SKIPPED)


def _set_last_copy_skipped(v: bool) -> None:
    global _LAST_COPY_SKIPPED
    _LAST_COPY_SKIPPED = v


def _extract_workfile_remote_path(file_data: Optional[dict], task_data: dict) -> str:
    if file_data:
        # common keys seen in workfile widgets
        for k in ("path", "file_path", "workfile_path", "work_detail.file_path"):
            v = file_data.get(k) if isinstance(file_data, dict) else None
            if v:
                return str(v)

        # nested structure best-effort
        wd = file_data.get("work_detail") if isinstance(file_data, dict) else None
        if isinstance(wd, dict) and wd.get("file_path"):
            return str(wd["file_path"])

    # fallback: try from task payload (if you store “current workfile” anywhere)
    # TODO: wire your actual canonical location if present
    candidate = (
        (task_data or {}).get("pipeline", {}).get("paths", {}).get("workfile")
        or (task_data or {}).get("pipeline", {}).get("paths", {}).get("workfile_path")
    )
    return str(candidate) if candidate else ""


def _extract_reference_path(ref: Dict[str, Any]) -> str:
    # Best-effort: support multiple DTO shapes
    for k in (
        "resolved_path",
        "path",
        "file_path",
        "publish_path",
        "source_path",
        "cache_path",
        "dir_path",
        "directory",
    ):
        v = ref.get(k)
        if v:
            return str(v)
    return ""


def _norm(p: str) -> str:
    return (p or "").replace("\\", "/").rstrip("/")


def _map_remote_to_local(remote_path: str, path_map: List[dict]) -> str:
    """
    Uses env.path_map rules to map server/UNC paths into local Z: cache paths.

    Expected rule examples (support several shapes, best-effort):
      - {"from": "/srv/stor/projects", "to": "Z:/projects"}
      - {"src_prefix": "//10.10.19.52/HiddenIsland", "dst_prefix": "Z:/HiddenIsland"}
      - {"remote": "/srv/stor/projects/HiddenIsland", "local": "Z:/HiddenIsland"}
    """
    rp = _norm(remote_path)

    # Already local
    if rp.lower().startswith("z:/"):
        return rp.replace("/", "\\")

    for rule in (path_map or []):
        if not isinstance(rule, dict):
            continue

        src = rule.get("from") or rule.get("src_prefix") or rule.get("remote") or ""
        dst = rule.get("to") or rule.get("dst_prefix") or rule.get("local") or ""
        if not src or not dst:
            continue

        src_n = _norm(str(src))
        if rp.lower().startswith(src_n.lower()):
            mapped = str(dst).rstrip("/\\") + rp[len(src_n):]
            # return Windows-friendly
            return mapped.replace("/", "\\")

    # last-resort fallback (TODO: replace with pipeline_core PathResolver if available)
    # If remote looks like /srv/... try mapping to Z:\ with same tail after '/srv/stor/projects'
    anchor = "/srv/stor/projects"
    if rp.lower().startswith(anchor):
        tail = rp[len(anchor):]
        return ("Z:/projects" + tail).replace("/", "\\")

    return ""


def _default_rclone_flags() -> list[str]:
    # Keep small + safe. Add more only if you’ve tested them in your environment.
    return [
        "--exclude", ".DS_Store",
        "--retries", "3",
        "--low-level-retries", "10",
        "--transfers", "4",
        "--checkers", "8",
        "--update",
    ]


_RCLONE_FILTER_FLAGS_WITH_ARG = {
    "--exclude", "--include", "--filter",
    "--exclude-from", "--include-from", "--filter-from",
    "--files-from", "--files-from-raw",
}
_RCLONE_FILTER_FLAGS_NO_ARG = {
    "--delete-excluded", "--ignore-case",
}

def _sanitize_rclone_flags_for_copyto(flags: list[str]) -> list[str]:
    """
    rclone copyto DOES NOT allow filter flags.
    Remove any filter-related flags (and their value if applicable).
    """
    out: list[str] = []
    skip_next = False
    for f in (flags or []):
        if skip_next:
            skip_next = False
            continue

        if f in _RCLONE_FILTER_FLAGS_WITH_ARG:
            skip_next = True
            continue

        if f in _RCLONE_FILTER_FLAGS_NO_ARG:
            continue

        out.append(f)
    return out


def _copy_via_rclone(src: str, dst: str, *, is_dir: bool, logger=None) -> None:
    """
    Uses rclone for both files and directories.
    - file: copyto src dst   (NO FILTER FLAGS)
    - dir : copy src_dir dst_dir
    """
    src_p = (src or "").replace("\\", "/")
    dst_p = (dst or "").replace("\\", "/")

    flags = _default_rclone_flags()

    if is_dir:
        os.makedirs(dst_p, exist_ok=True)
        # copy supports filters; keep flags as-is
        rc = copy_through_rclone(rclone_command="copy", src=src_p, dest=dst_p, flags=flags)
    else:
        parent = os.path.dirname(dst_p)
        if parent:
            os.makedirs(parent, exist_ok=True)

        # copyto does NOT support filters -> sanitize
        safe_flags = _sanitize_rclone_flags_for_copyto(flags)
        rc = copy_through_rclone(rclone_command="copyto", src=src_p, dest=dst_p, flags=safe_flags)

    if rc != 0:
        raise RuntimeError(f"rclone failed with exit code {rc} for {src_p} -> {dst_p}")


def _copy_idempotent(
    src: str,
    dst: str,
    *,
    logger=None,
    retries: int = 3,
    retry_sleep: float = 0.75,
    prefer_rclone: bool = False,
) -> None:
    """
    Copy file/dir with idempotency. Prefer rclone when requested.
    Falls back to shutil if rclone fails.

    IMPORTANT:
    - For rclone remotes (remote:/ftp:/sftp:...), os.path.exists/isfile/isdir will NOT work.
      We skip local preflight and rely on rclone --update.
    """
    _set_last_copy_skipped(False)

    src_raw = (src or "").strip()
    dst_raw = (dst or "").strip()

    if not src_raw or not dst_raw:
        raise RuntimeError("Empty src/dst")

    # If src is an rclone remote, we must use rclone (no local os.path checks)
    if is_remote_scheme(src_raw):
        # Best-effort: decide file vs dir by dst extension
        is_dir = (os.path.splitext(dst_raw)[1] == "")
        _copy_via_rclone(src_raw, dst_raw, is_dir=is_dir, logger=logger)
        return

    # Normal filesystem paths (UNC, drives, local)
    src_fs = os.path.normpath(src_raw)
    dst_fs = os.path.normpath(dst_raw)

    if not os.path.exists(src_fs):
        raise FileNotFoundError(src_fs)

    # Idempotency checks first
    if os.path.isfile(src_fs):
        if _is_file_uptodate(src_fs, dst_fs):
            _set_last_copy_skipped(True)
            return
        src_is_dir = False
    elif os.path.isdir(src_fs):
        if _is_dir_marker_uptodate(src_fs, dst_fs):
            _set_last_copy_skipped(True)
            return
        src_is_dir = True
    else:
        raise RuntimeError(f"Unsupported path type: {src_fs}")

    # Try rclone if preferred
    if prefer_rclone:
        try:
            _copy_via_rclone(src_fs, dst_fs, is_dir=src_is_dir, logger=logger)
            return
        except Exception as e:
            if logger:
                logger.warning("rclone copy failed; falling back to shutil: %s", e)

    # Fallback: shutil-based
    if src_is_dir:
        os.makedirs(dst_fs, exist_ok=True)
        _copy_dir_best_effort(src_fs, dst_fs, retries=retries, retry_sleep=retry_sleep, logger=logger)
    else:
        os.makedirs(os.path.dirname(dst_fs), exist_ok=True)
        _copy_file_with_retries(src_fs, dst_fs, retries=retries, retry_sleep=retry_sleep, logger=logger)


def _is_file_uptodate(src: str, dst: str) -> bool:
    if not os.path.exists(dst):
        return False
    try:
        return (os.path.getsize(dst) == os.path.getsize(src)) and (os.path.getmtime(dst) >= os.path.getmtime(src))
    except Exception:
        return False


def _is_dir_marker_uptodate(src_dir: str, dst_dir: str) -> bool:
    # Minimal idempotency: if dst exists and is newer than src, skip.
    # TODO: replace with manifest-based sync if needed.
    if not os.path.exists(dst_dir):
        return False
    try:
        return os.path.getmtime(dst_dir) >= os.path.getmtime(src_dir)
    except Exception:
        return False


def _copy_file_with_retries(src: str, dst: str, *, retries: int, retry_sleep: float, logger=None) -> None:
    last_err: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            shutil.copy2(src, dst)
            return
        except Exception as e:
            last_err = e
            if logger:
                logger.warning("copy2 failed (attempt %s/%s): %s -> %s (%s)", attempt, retries, src, dst, e)
            time.sleep(retry_sleep)
    raise last_err or RuntimeError("copy2 failed")


def _copy_dir_best_effort(src_dir: str, dst_dir: str, *, retries: int, retry_sleep: float, logger=None) -> None:
    # If dst exists, we do an “overlay” copy (best-effort), not a destructive mirror.
    # TODO: if you need true mirror semantics, use rclone sync with filters.
    os.makedirs(dst_dir, exist_ok=True)

    last_err: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            for root, dirs, files in os.walk(src_dir):
                rel = os.path.relpath(root, src_dir)
                target_root = os.path.join(dst_dir, rel) if rel != "." else dst_dir
                os.makedirs(target_root, exist_ok=True)
                for f in files:
                    s = os.path.join(root, f)
                    d = os.path.join(target_root, f)
                    if _is_file_uptodate(s, d):
                        continue
                    shutil.copy2(s, d)
            return
        except Exception as e:
            last_err = e
            if logger:
                logger.warning("copy dir failed (attempt %s/%s): %s -> %s (%s)", attempt, retries, src_dir, dst_dir, e)
            time.sleep(retry_sleep)

    raise last_err or RuntimeError("copy dir failed")


def _latest_maya_in_work_dir(work_dir: str) -> str:
    """
    Pick latest .ma/.mb by mtime (fallback if version parsing isn't reliable).
    """
    d = Path((work_dir or "").replace("\\", "/"))
    if not d.exists() or not d.is_dir():
        return ""
    cands = [p for p in d.iterdir() if p.is_file() and p.suffix.lower() in {".ma", ".mb"}]
    if not cands:
        return ""
    cands.sort(key=lambda p: (p.stat().st_mtime, p.name), reverse=True)
    return cands[0].as_posix()


def _resolve_dep_src_dst(dep_path: str, *, base_dir: str, path_map: List[dict]) -> tuple[str, str]:
    """
    Returns (src_remote_or_unc, dst_local_z).
    Supports dep paths that are:
      - Z:/...         => derive remote via _map_local_to_remote
      - //server/...   => derive local via _map_remote_to_local
      - relative       => resolve against base_dir first
      - other drives   => we don't download; treat as local-only
    """
    p = _norm(dep_path)
    if not p:
        return ("", "")

    # relative -> make absolute against the maya file directory
    if not (p.startswith("//") or p.startswith("\\\\") or _DRIVE_RE.match(p) or is_remote_scheme(p)):
        p = _norm((Path(base_dir) / p).as_posix())

    # Local Z: -> remote UNC/src + local dst (same as p)
    if p.lower().startswith("z:/"):
        dst_local = p
        src_remote = _map_local_to_remote(dst_local, path_map)
        return (src_remote, dst_local)

    # Other local drives (C:/ etc) -> don't try download
    if _DRIVE_RE.match(p) and not p.lower().startswith("z:/"):
        return ("", p)

    # UNC or rclone remote -> map to local
    if p.startswith("//") or p.startswith("\\\\") or is_remote_scheme(p):
        src_remote = p
        dst_local = _map_remote_to_local(src_remote, path_map)
        return (src_remote, dst_local)

    # last fallback: try mapping as remote anyway
    src_remote = p
    dst_local = _map_remote_to_local(src_remote, path_map)
    return (src_remote, dst_local)


def _download_maya_deps_bfs(
    *,
    entry_local_maya: str,
    task_data: Dict[str, Any],
    path_map: List[dict],
    mayapy: str,
    summary: DownloadSummary,
    progress_cb: Optional[ProgressCB],
    logger,
    prefer_rclone: bool,
    check_ftp_connection_fn=None,
    max_maya_files: int = 500,
    max_total_deps: int = 8000,
) -> None:
    """
    BFS recursion:
      queue = [entry maya]
      pop -> parse deps
      for each dep:
        map (remote_src, local_dst)
        download (UDIM-aware)
        if local_dst is maya and exists -> enqueue
    """
    from pipeline.infra.maya.maya_file_ops import discover_maya_dependencies, is_maya_file

    q = deque([_norm(entry_local_maya)])
    seen_maya: set[str] = set()

    # Dedup for normal deps
    seen_copy: set[tuple[str, str]] = set()

    # Dedup for UDIM sets (local to this call)
    seen_udim_groups: set[str] = set()

    maya_count = 0
    dep_count = 0  # counts “copy operations” (normal deps + UDIM sets as 1)

    def _udim_group_key(src_path: str) -> str:
        src_n = (src_path or "").replace("\\", "/")
        bn = os.path.basename(src_n)
        parsed = _parse_udim_tile_name(bn)
        if not parsed:
            return src_n.lower()
        base, sep, _u, ext = parsed
        return f"{os.path.dirname(src_n).lower()}|{base.lower()}|{sep}|{ext.lower()}"

    while q:
        if maya_count >= max_maya_files:
            summary.failed.append({"error": "max_maya_files_reached", "limit": max_maya_files})
            summary.failed_count += 1
            return

        local_maya = _norm(q.popleft())
        if not local_maya:
            continue

        key_m = local_maya.lower()
        if key_m in seen_maya:
            continue
        seen_maya.add(key_m)
        maya_count += 1

        base_dir = str(Path(local_maya).parent)

        if progress_cb:
            progress_cb(
                f"Scanning deps: {Path(local_maya).name}",
                maya_count,
                max(maya_count + len(q), 1),
            )

        try:
            deps = discover_maya_dependencies(local_maya, mayapy=mayapy) or []
        except Exception as e:
            summary.failed.append({"error": f"dep_parse_failed: {e}", "path": local_maya})
            summary.failed_count += 1
            continue

        for dep in deps:
            src_remote, dst_local = _resolve_dep_src_dst(dep, base_dir=base_dir, path_map=path_map)

            # local-but-not-Z => don't download
            if not src_remote and dst_local:
                continue

            if not src_remote or not dst_local:
                summary.missing.append({"reason": "unmappable", "path": dep, "from": local_maya})
                continue

            # ---- UDIM handling ----
            if _is_udim_candidate(src_remote) or _is_udim_candidate(dst_local):
                gk = _udim_group_key(src_remote)
                if gk in seen_udim_groups:
                    continue
                seen_udim_groups.add(gk)

                dep_count += 1
                if dep_count >= max_total_deps:
                    summary.failed.append({"error": "max_total_deps_reached", "limit": max_total_deps})
                    summary.failed_count += 1
                    return

                if progress_cb:
                    progress_cb(f"Downloading UDIM set ({dep_count})", dep_count, max(dep_count + 1, 1))

                # Preflight only for true rclone remotes
                if check_ftp_connection_fn and is_remote_scheme(src_remote):
                    if not check_ftp_connection_fn(check_FTP_conn=True):
                        summary.failed.append({"error": "ftp_connection_failed", "path": src_remote, "udim": True})
                        summary.failed_count += 1
                        continue

                try:
                    dl, sk = _copy_udim_set(
                        src_remote,
                        dst_local,
                        prefer_rclone=prefer_rclone,
                        logger=logger,
                        check_ftp_connection_fn=check_ftp_connection_fn,
                    )
                    summary.downloaded_count += dl
                    summary.skipped_count += sk
                except FileNotFoundError:
                    summary.missing.append({"reason": "source_not_found_udim", "path": src_remote, "to": dst_local})
                except Exception as e:
                    summary.failed.append({"error": str(e), "path": src_remote, "to": dst_local, "udim": True})
                    summary.failed_count += 1

                # UDIM textures are not Maya files => no recursion enqueue
                continue

            # ---- Normal dep (dedupe BEFORE copying) ----
            pair = (src_remote.lower(), dst_local.lower())
            if pair in seen_copy:
                continue
            seen_copy.add(pair)

            dep_count += 1
            if dep_count >= max_total_deps:
                summary.failed.append({"error": "max_total_deps_reached", "limit": max_total_deps})
                summary.failed_count += 1
                return

            if progress_cb:
                progress_cb(f"Downloading deps ({dep_count})", dep_count, max(dep_count + 1, 1))

            # Preflight only for true rclone remotes
            if check_ftp_connection_fn and is_remote_scheme(src_remote):
                if not check_ftp_connection_fn(check_FTP_conn=True):
                    summary.failed.append({"error": "ftp_connection_failed", "path": src_remote})
                    summary.failed_count += 1
                    continue

            try:
                _copy_idempotent(src_remote, dst_local, logger=logger, prefer_rclone=prefer_rclone)
                if _was_last_copy_skipped():
                    summary.skipped_count += 1
                else:
                    summary.downloaded_count += 1
            except FileNotFoundError:
                summary.missing.append({"reason": "source_not_found", "path": src_remote, "to": dst_local})
                continue
            except Exception as e:
                summary.failed.append({"error": str(e), "path": src_remote, "to": dst_local})
                summary.failed_count += 1
                continue

            # recurse only on Maya deps that now exist locally
            dst_norm = _norm(dst_local)
            if is_maya_file(dst_norm) and Path(dst_norm).exists():
                q.append(dst_norm)

    summary.missing_count = len(summary.missing)


