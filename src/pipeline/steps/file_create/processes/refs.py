from __future__ import annotations

import os
from typing import Any, Dict, Set, Optional
import re

from .registry import process
from ..utils.deps import normalize_dependency_inputs, _dep_namespace
from ..utils.tokens import ctx_tokens, resolve_template

import re
from pathlib import Path


_NS_CLEAN_RE = re.compile(r"[^0-9a-zA-Z_]+")

def _ctx_get(ctx: Any, key: str, default=None):
    if hasattr(ctx, "get"):
        return ctx.get(key, default)
    return getattr(ctx, key, default)

def _sanitize_ns(s: str) -> str:
    s = (s or "").strip()
    s = _NS_CLEAN_RE.sub("_", s)
    if not s:
        s = "REF"
    if s[0].isdigit():
        s = f"N_{s}"
    return s

def _select_ns_rule(ctx: Any, dep_kind: str, dep_role: Optional[str]) -> Dict[str, Any]:
    rules = _ctx_get(ctx, "reference_namespaces", {}) or {}
    upstream_by_role = rules.get("upstream_by_role") or {}
    if dep_role and dep_role in upstream_by_role:
        return upstream_by_role[dep_role] or {}
    return rules.get(dep_kind) or {}

def _apply_pattern(pattern: str, tokens: Dict[str, str]) -> str:
    out = pattern or ""
    for k, v in tokens.items():
        out = out.replace("${" + k + "}", v)
    return out

def _build_dep_namespace(ctx: Any, d: Any, used: set, counters: Dict[str, int]) -> str:
    meta = getattr(d, "meta", None) or {}
    dep_kind = getattr(d, "kind", "") or ""
    dep_role = getattr(d, "role", None)

    rule = _select_ns_rule(ctx, dep_kind, dep_role)
    pattern = str(rule.get("pattern") or "").strip() or "${ENTITY_NAME}"
    start = int(rule.get("start") or 1)
    padding = int(rule.get("padding") or 2)

    # 1) If backend provided an explicit namespace, use it AS-IS
    explicit_ns = meta.get("namespace")
    if explicit_ns:
        ns = _sanitize_ns(str(explicit_ns))
        if ns in used:
            i = 2
            cand = f"{ns}_{i:02d}"
            while cand in used:
                i += 1
                cand = f"{ns}_{i:02d}"
            ns = cand
        used.add(ns)
        return ns

    # 2) Otherwise choose a clean base name (prefer shortest candidate like "BTL")
    candidates = meta.get("entity_name_candidates") or []
    base = (
        getattr(d, "entity_name", None)
        or meta.get("entity_name")
        or (min(candidates, key=lambda s: (s.count("_"), len(s))) if candidates else None)
        or Path(getattr(d, "path", "") or "").stem
        or "REF"
    )
    base = _sanitize_ns(str(base))

    # 3) Handle both 0-based and 1-based occurrence_index
    occ = meta.get("occurrence_index", None)
    if occ is not None:
        occ_int = int(occ)
        if occ_int == 0:
            idx_int = start  # 0-based
        elif start == 1:
            idx_int = occ_int  # 1-based
        else:
            idx_int = start + occ_int
    else:
        idx_int = counters.get(base, start)
        counters[base] = idx_int + 1

    idx_str = str(idx_int).zfill(padding)

    tokens = {
        "ENTITY_NAME": base,
        "INDEX": idx_str,
        "ROLE": _sanitize_ns(str(dep_role or "")) if dep_role else "",
        "KIND": _sanitize_ns(dep_kind),
    }

    ns = _sanitize_ns(_apply_pattern(pattern, tokens))

    if ns in used:
        i = 2
        cand = f"{ns}_{i:02d}"
        while cand in used:
            i += 1
            cand = f"{ns}_{i:02d}"
        ns = cand

    used.add(ns)
    return ns


def _maya_path(p: str) -> str:
    return (p or "").replace("\\", "/")


def _unique_dag(base: str) -> str:
    import maya.cmds as cmds  # type: ignore
    if not cmds.objExists(base):
        return base
    i = 1
    while True:
        n = f"{base}_{i:02d}"
        if not cmds.objExists(n):
            return n
        i += 1


def _reference_grouped(path: str, namespace: str, parent_grp: str) -> None:
    import maya.cmds as cmds  # type: ignore
    path = _maya_path(path)
    grp_name = _unique_dag(f"{namespace}_REF_GRP")

    cmds.file(
        path,
        r=True,
        namespace=namespace,
        mergeNamespacesOnClash=False,
        groupReference=True,
        groupName=grp_name,
        options="v=0",
        ignoreVersion=True,
    )
    if parent_grp:
        try:
            cmds.parent(grp_name, parent_grp)
        except Exception:
            pass


def _ensure_group_path(dag_path: str) -> str:
    import maya.cmds as cmds  # type: ignore

    dag_path = (dag_path or "").strip()
    if not dag_path:
        return dag_path
    if dag_path.startswith("|"):
        dag_path = dag_path[1:]

    parts = [p for p in dag_path.split("|") if p]
    if not parts:
        return dag_path

    cur = parts[0]
    if not cmds.objExists(cur):
        cmds.group(em=True, name=cur)

    for p in parts[1:]:
        full = f"{cur}|{p}"
        if cmds.objExists(full) or cmds.objExists(p):
            cur = full if cmds.objExists(full) else p
            continue
        node = cmds.group(em=True, name=p)
        try:
            cmds.parent(node, cur)
        except Exception:
            pass
        cur = f"{cur}|{p}"

    return parts[-1]


def _match_parent_key(parent_mapping: Dict[str, Any], *needles: str) -> Optional[str]:
    # case-insensitive contains match
    for k in parent_mapping.keys():
        lk = str(k).lower()
        if any(n in lk for n in needles):
            return k
    return None


def _norm_key(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "", s)  # "__CHAR__" -> "char"
    return s

def _match_parent_key(parent_mapping: Dict[str, Any], aliases: list[str], contains: list[str]) -> Optional[str]:
    # Build normalized lookup
    norm_map = {_norm_key(str(k)): k for k in parent_mapping.keys()}

    # 1) exact alias match (normalized)
    for a in aliases:
        k = norm_map.get(_norm_key(a))
        if k:
            return k

    # 2) contains match (normalized)
    for k in parent_mapping.keys():
        nk = _norm_key(str(k))
        if any(_norm_key(c) in nk for c in contains):
            return k

    return None

def _find_mapping_key(meta: Dict[str, Any], parent_mapping: Dict[str, Any]) -> Optional[str]:
    # 1) direct candidates (exact / case-insensitive)
    candidates = [
        meta.get("entity_subtype"),
        meta.get("entity_subtype_code"),
        meta.get("asset_type"),
    ]
    candidates = [str(c).strip() for c in candidates if c]

    for c in candidates:
        if c in parent_mapping:
            return c

    pm_keys = {str(k).lower(): k for k in parent_mapping.keys()}
    for c in candidates:
        k = pm_keys.get(c.lower())
        if k:
            return k

    # 2) alias mapping from asset_type -> common group keys
    at = str(meta.get("asset_type") or "").strip().upper()

    if at == "CHR":
        return _match_parent_key(
            parent_mapping,
            aliases=["CHR", "Characters", "__CHAR__", "__CHARACTERS__", "CHAR", "CHARACTERS"],
            contains=["chr", "char", "character"],
        )
    if at == "PRP":
        return _match_parent_key(
            parent_mapping,
            aliases=["PRP", "Props", "__PROP__", "__PROPS__", "PROP", "PROPS"],
            contains=["prp", "prop"],
        )
    if at == "ENV":
        return _match_parent_key(
            parent_mapping,
            aliases=["ENV", "Environment", "__ENV__", "__ENVIRONMENT__", "BG", "SET"],
            contains=["env", "environment", "bg", "bkg", "set"],
        )
    if at == "CAM":
        return _match_parent_key(
            parent_mapping,
            aliases=["CAM", "Camera", "__CAM__", "__CAMERA__"],
            contains=["cam", "camera"],
        )

    return None


@process("assetReference")
def assetReference(ctx: Any) -> None:
    import maya.cmds as cmds  # type: ignore

    asset_deps = getattr(ctx, "asset_dependencies", None) or ctx.get("asset_dependencies") or {}
    if not asset_deps:
        print("[assetReference] No asset dependencies found, skipping")
        return

    for _subtype, paths in asset_deps.items():
        for path in (paths or []):
            if not os.path.exists(path):
                cmds.warning(f"[assetReference] Missing reference file: {path}")
                continue
            namespace = os.path.splitext(os.path.basename(path))[0]
            try:
                cmds.file(_maya_path(path), reference=True, namespace=namespace, returnNewNodes=True)
            except Exception as e:
                cmds.warning(f"[assetReference] Failed to reference {path}: {e}")


@process("shotReference", requires_keys=("group_templates", "entity_type", "dependency_inputs"))
def shotReference(ctx: Any) -> None:
    import maya.cmds as cmds  # type: ignore

    templates: Dict[str, Any] = _ctx_get(ctx, "group_templates", {}) or {}
    entity_type = str(_ctx_get(ctx, "entity_type", "") or "").strip()
    entity_template = (templates.get("templates") or {}).get(entity_type) or {}
    parent_mapping = entity_template.get("parent_mapping") or {}

    if not parent_mapping:
        cmds.warning("[shotReference] No parent_mapping in group_templates")
        return

    toks, _warns = ctx_tokens(ctx)

    raw = _ctx_get(ctx, "dependency_inputs", None) or []
    deps = normalize_dependency_inputs(raw)

    used: Set[str] = set()
    counters: Dict[str, int] = {}

    for d in deps:
        if d.kind not in ("asset_file", "task_file", "shot_workfile"):
            continue
        if not os.path.exists(d.path):
            cmds.warning(f"[shotReference] Missing ref: {d.path}")
            continue

        meta = getattr(d, "meta", None) or {}
        map_key = _find_mapping_key(meta, parent_mapping)
        if not map_key:
            cmds.warning(f"[shotReference] No parent mapping key for dep meta: {meta}")
            continue

        mapped_group = parent_mapping.get(map_key)
        parent_group = resolve_template(str(mapped_group), toks, strict=False)

        # ensure groups exist (THIS is the big missing piece)
        _ensure_group_path(parent_group)

        if not cmds.objExists(parent_group):
            cmds.warning(f"[shotReference] Parent group missing: {parent_group}")
            continue

        ns = _build_dep_namespace(ctx, d, used=used, counters=counters)

        try:
            _reference_grouped(d.path, namespace=ns, parent_grp=parent_group)
            print(f"[shotReference] Referenced {d.path} as {ns} under {parent_group}")
        except Exception as e:
            cmds.warning(f"[shotReference] Failed to reference {d.path}: {e}")


@process("referenceCameraRig", requires_keys=("camera_rig",))
def referenceCameraRig(ctx: Any) -> None:
    import maya.cmds as cmds  # type: ignore

    cam_path = ctx.get("camera_rig")
    if not cam_path:
        return
    if not os.path.exists(cam_path):
        cmds.warning(f"[referenceCameraRig] Missing camera rig: {cam_path}")
        return

    for g in ("__CAM__", "__CHAR__", "__PROP__"):
        if not cmds.objExists(g):
            cmds.group(em=True, name=g)

    camrig_parent = "CAM_RIG_GRP"
    if not cmds.objExists(camrig_parent):
        camrig_parent = cmds.group(em=True, name=camrig_parent)
        try:
            cmds.parent(camrig_parent, "__CAM__")
        except Exception:
            pass

    ns = ctx.get("camera_ns") or "CAMRIG"
    grp_name = _unique_dag(f"{ns}_REF_GRP")
    ref_node = cmds.file(
        _maya_path(cam_path),
        r=True,
        namespace=str(ns),
        mergeNamespacesOnClash=False,
        groupReference=True,
        groupName=grp_name,
        options="v=0",
        ignoreVersion=True,
    )
    try:
        cmds.parent(grp_name, camrig_parent)
    except Exception:
        pass

    # store render camera (best-effort)
    try:
        ref_nodes = cmds.referenceQuery(ref_node, nodes=True, dagPath=True) or []
        cam_shapes = cmds.ls(ref_nodes, type="camera") or []
        if cam_shapes:
            def _short(n: str) -> str:
                n = n.split("|")[-1]
                return n.split(":")[-1].lower()

            preferred = [c for c in cam_shapes if "rendercamerashape" in _short(c)]
            shape = preferred[0] if preferred else cam_shapes[0]
            xform = cmds.listRelatives(shape, parent=True, fullPath=False) or []
            if xform:
                ctx.render_camera_transform = xform[0]
                ctx.render_camera_shape = shape
    except Exception:
        pass


@process("referenceDependencyInputs", requires_keys=("dependency_inputs",))
def referenceDependencyInputs(ctx: Any) -> None:
    import maya.cmds as cmds  # type: ignore

    raw = _ctx_get(ctx, "dependency_inputs", None) or []
    deps = normalize_dependency_inputs(raw)

    used: Set[str] = set()
    counters: Dict[str, int] = {}

    for d in deps:
        if d.kind not in ("asset_file", "task_file", "shot_workfile"):
            continue

        ns = _build_dep_namespace(ctx, d, used=used, counters=counters)

        try:
            cmds.file(
                _maya_path(d.path),
                reference=True,
                namespace=ns,
                mergeNamespacesOnClash=False,
                ignoreVersion=True,
                options="v=0;",
            )
        except Exception as e:
            cmds.warning(f"[referenceDependencyInputs] Failed {d.path}: {e}")