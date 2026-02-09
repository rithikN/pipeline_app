# services/wfh_mapping.py
import os
import subprocess
from pathlib import Path
from PySide6.QtCore import QSettings
import threading


_LOCK = threading.Lock()
_Z_READY: set[str] = set()


def resolve_local_cache_root(show_code: str) -> str:
    show = (show_code or "SHOW").strip().upper()

    # 1) env first
    env = os.environ.get("PIPELINE_LOCAL_CACHE_ROOT") or os.environ.get(f"{show}_LOCAL_CACHE_ROOT")
    if env:
        return str(Path(env).expanduser())

    # 2) saved setting
    qs = QSettings("PCGI", "PipelineApp")
    saved = qs.value(f"local_cache_root/{show}", "", type=str)
    if saved:
        return saved

    # 3) safe fallback
    fallback = str(Path.home() / "PipelineCache" / show)
    return fallback

def persist_local_cache_root(show_code: str, root: str) -> None:
    show = (show_code or "SHOW").strip().upper()
    qs = QSettings("PCGI", "PipelineApp")
    qs.setValue(f"local_cache_root/{show}", root)

def _current_subst_target(drive: str = "Z:") -> str:
    """
    Returns current subst target for drive, or "" if not subst-mapped.
    """
    try:
        out = subprocess.run(["subst"], check=False, capture_output=True, text=True).stdout or ""
        # example: "Z:\: => C:\PipelineCache\HLD"
        for line in out.splitlines():
            if line.upper().startswith(f"{drive.upper()}\\"):
                parts = line.split("=>", 1)
                return parts[1].strip() if len(parts) == 2 else ""
    except Exception:
        pass
    return ""

def ensure_z_subst(local_cache_root: str) -> None:
    """
    Map Z: -> local_cache_root using subst.

    IMPORTANT:
    - Now idempotent: if Z already points to the same target, do nothing.
    - Avoids repeated "subst /D" which was causing UI stalls / domino calls.
    """
    p = Path(local_cache_root)
    p.mkdir(parents=True, exist_ok=True)

    # deadline hardcode (ok for now)
    (p / "HiddenIsland_Server").mkdir(parents=True, exist_ok=True)
    (p / "HiddenIsland_Software").mkdir(parents=True, exist_ok=True)

    desired = str(p)
    current = _current_subst_target("Z:")

    # already mapped to desired -> do nothing
    try:
        if current and Path(current).resolve() == Path(desired).resolve():
            return
    except Exception:
        # if resolve fails, just remap safely
        pass

    # clear any existing Z mappings (only if changing)
    subprocess.run(["subst", "Z:", "/D"], check=False, capture_output=True, text=True)
    subprocess.run(["net", "use", "Z:", "/delete", "/y"], check=False, capture_output=True, text=True)

    subprocess.run(["subst", "Z:", desired], check=True)


def ensure_wfh_z_for_show(show_code: str) -> str:
    show = (show_code or "HLD").strip().upper()
    print(1111111111111111456)
    if show in _Z_READY:
        return resolve_local_cache_root(show)

    with _LOCK:
        if show in _Z_READY:
            return resolve_local_cache_root(show)
        root = resolve_local_cache_root(show)
        ensure_z_subst(root)
        _Z_READY.add(show)
        return root

