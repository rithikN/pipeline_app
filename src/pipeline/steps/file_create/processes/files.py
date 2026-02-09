from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Optional, List, Tuple

from .registry import process


_VER_RE = re.compile(r"_V(\d{3,})\b", re.IGNORECASE)


def _maya_path(p: str) -> str:
    return (p or "").replace("\\", "/")


def _maya_file_type_from_ext(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return "mayaBinary" if ext == ".mb" else "mayaAscii"


def _workfile_path(ctx: Any) -> Optional[str]:
    """
    FINAL CONTRACT:
      - ctx["maya_file_path"]
    """
    p = ctx.get("maya_file_path")
    return str(p) if p else None


def _version_from_path(p: str) -> int:
    m = _VER_RE.search(os.path.basename(p or ""))
    return int(m.group(1)) if m else -1


def _pick_dependency_publish_path(ctx: Any, role: str = "lay") -> Optional[str]:
    """
    NEW CONTRACT:
      - ctx["dependency_inputs"] : list[dict]
        Each dict should contain:
          - path (str)
          - role or task_code (e.g. "LAY")
          - optional meta.version_int (int)
    """
    role = (role or "lay").strip().lower()
    deps = ctx.get("dependency_inputs") or []
    if not isinstance(deps, list) or not deps:
        return None

    candidates: List[Tuple[int, str]] = []

    for d in deps:
        if not isinstance(d, dict):
            continue

        d_role = (d.get("role") or d.get("task_code") or "").strip().lower()
        if d_role != role:
            continue

        path = d.get("path")
        if not path:
            continue

        meta = d.get("meta") or {}
        ver = meta.get("version_int")
        if not isinstance(ver, int):
            ver = _version_from_path(str(path))

        candidates.append((ver, str(path)))

    if not candidates:
        return None

    candidates.sort(key=lambda t: t[0], reverse=True)  # latest first
    return candidates[0][1]


@process("saveEmptyFile")
def saveEmptyFile(ctx: Any) -> None:
    """
    Legacy behavior:
      - new empty scene
      - rename to maya_file_path
      - save
      - print
    """
    import maya.cmds as cmds  # type: ignore

    out_path = _workfile_path(ctx)
    if not out_path:
        cmds.warning("[saveEmptyFile] ERROR: payload missing 'maya_file_path'")
        return

    # Ensure parent exists (safe, still using final key only)
    try:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    out_path = _maya_path(out_path)
    cmds.file(new=True, force=True)
    cmds.file(rename=out_path)
    cmds.file(save=True, force=True, type=_maya_file_type_from_ext(out_path))
    print("[saveEmptyFile] Empty scene created")


@process("saveFile")
def saveFile(ctx: Any) -> None:
    """
    Legacy behavior:
      - rename to maya_file_path
      - save
      - print
    """
    import maya.cmds as cmds  # type: ignore

    out_path = _workfile_path(ctx)
    if not out_path:
        cmds.warning("[saveFile] ERROR: payload missing 'maya_file_path'")
        return

    try:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    out_path = _maya_path(out_path)
    cmds.file(rename=out_path)
    cmds.file(save=True, force=True, type=_maya_file_type_from_ext(out_path))
    print(f"[saveFile] Saved: {out_path}")


@process("cloneUpstreamShotPublishFile")
def cloneUpstreamShotPublishFile(ctx: Any) -> None:
    """
    (dependency_inputs-only):
      - opens upstream publish in Maya (from dependency_inputs)
      - save-as to ctx["maya_file_path"]

    FINAL CONTRACT:
      - ctx["maya_file_path"]
      - ctx["dependency_inputs"]
      - optional ctx["upstream_role"] (default "lay")
    """
    import maya.cmds as cmds  # type: ignore

    dst = _workfile_path(ctx)
    if not dst:
        cmds.warning("[cloneUpstreamShotPublishFile] No maya_file_path in ctx")
        return

    # ensure output folder exists
    try:
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    role = (ctx.get("upstream_role") or "lay").strip().lower()
    src = _pick_dependency_publish_path(ctx, role=role)

    if not src:
        cmds.warning(
            f"[cloneUpstreamShotPublishFile] No upstream publish found in dependency_inputs for role={role!r}"
        )
        return

    if not os.path.exists(str(src)):
        cmds.warning(f"[cloneUpstreamShotPublishFile] Upstream published file missing: {src}")
        return

    try:
        cmds.file(new=True, force=True)
        cmds.file(str(src), o=True, force=True, ignoreVersion=True, prompt=False)

        cmds.file(rename=_maya_path(dst))
        cmds.file(save=True, force=True, type=_maya_file_type_from_ext(dst))

        print(f"[cloneUpstreamShotPublishFile] Cloned publish {src} -> {dst}")
    except Exception as e:
        cmds.warning(f"[cloneUpstreamShotPublishFile] Failed: {e}")


@process("cloneLayoutPublishToAnm")
def cloneLayoutPublishToAnm(ctx: Any) -> None:
    """
    Convenience wrapper:
      - forces upstream_role="lay"
      - then runs cloneUpstreamShotPublishFile
    """
    # If ctx is your Context object, it likely supports set(); if not, this still works as long as upstream_role isn't needed elsewhere.
    prev = ctx.get("upstream_role")
    if hasattr(ctx, "set"):
        ctx.set("upstream_role", "lay")
        cloneUpstreamShotPublishFile(ctx)
        ctx.set("upstream_role", prev)
    else:
        # fallback: just rely on default "lay"
        cloneUpstreamShotPublishFile(ctx)


@process("importMasterTemplate")
def importMasterTemplate(ctx: Any) -> None:
    import maya.cmds as cmds  # type: ignore

    path = ctx.get("master_template_path")
    if not path:
        return

    cmds.file(str(path), i=True, ignoreVersion=True, mergeNamespacesOnClash=False, options="v=0;")