from __future__ import annotations

from typing import Any, List, Optional, Set

from .registry import process
from ..utils.deps import normalize_dependency_inputs, _dep_namespace
from ..utils.paths import norm_maya_path


def _ensure_plugins() -> None:
    import maya.cmds as cmds  # type: ignore
    for plugin in ("AbcImport",):
        try:
            if not cmds.pluginInfo(plugin, q=True, loaded=True):
                cmds.loadPlugin(plugin)
        except Exception:
            # Keep non-fatal to preserve production tolerance; if your old code raises, tighten here.
            pass


def _find_geo(ns: str) -> Optional[str]:
    import maya.cmds as cmds  # type: ignore
    # Prefer "ns:geo"
    cand = f"{ns}:geo" if ns else "geo"
    hits = cmds.ls(cand, long=True) or []
    if hits:
        return hits[0]
    # fallback: any transform ending with ":geo"
    hits = cmds.ls(f"{ns}:*", type="transform", long=True) or []
    for h in hits:
        if h.lower().endswith(":geo"):
            return h
    return None


def _abc_connect(cache_path: str, target: str) -> None:
    import maya.mel as mel  # type: ignore
    cp = norm_maya_path(cache_path).replace('"', '\\"')
    tg = target.replace('"', '\\"')
    mel.eval(f'AbcImport -mode import -connect "{tg}" "{cp}";')


@process("connectCachesFromDependencyInputs")
def connectCachesFromDependencyInputs(ctx: Any) -> None:
    """
    Connect caches (typically Alembic) from dependency_inputs to referenced geo.

    Expected kinds (payload-dependent):
      - shot_cache
      - shot_cache_dir
      - shot_cache_file
    """
    _ensure_plugins()

    raw = ctx.get("dependency_inputs", None) or []
    deps = normalize_dependency_inputs(raw)

    used: Set[str] = set()
    for d in deps:
        if d.kind not in ("shot_cache", "shot_cache_dir", "shot_cache_file"):
            continue

        ns = _dep_namespace(d.meta, used=used)
        geo = _find_geo(ns)
        if not geo:
            # Non-fatal warning to keep stable behavior; if your old code raises, tighten.
            try:
                import maya.cmds as cmds  # type: ignore
                cmds.warning(f"[file_create] No geo found for namespace '{ns}' to connect cache: {d.path}")
            except Exception:
                pass
            continue

        # If a directory is provided, your original code might scan for abc files.
        # We keep safe behavior: if it's a file, connect it; if it's a dir, no-op unless you extend.
        if d.path.lower().endswith(".abc"):
            _abc_connect(d.path, geo)