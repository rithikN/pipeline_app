# src/pipeline/infra/maya/maya_file_ops.py
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Iterable, List, Optional, Set

# --- .ma parsing (fast, no Maya needed) ---
# Maya reference lines typically look like:
# file -r -ns "X" -dr 1 -rfn "XRN" "Z:/path/file.ma";
_MA_REF_RE = re.compile(r'^\s*file\s+-r\b.*?"([^"]+)"\s*;', re.IGNORECASE)

# Texture-ish string attrs are messy; keep it best-effort and filtered by ext
# (You can tighten this later to specific attrs: fileTextureName/filename etc.)
_MA_STRING_PATH_RE = re.compile(r'"([^"]+)"')

_DEP_EXTS = (
    ".ma", ".mb", ".abc", ".fbx", ".obj",
    ".usd", ".usda", ".usdc",
    ".exr", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".tx",
    ".wav", ".mp3",
)

def is_maya_file(path: str) -> bool:
    p = (path or "").lower()
    return p.endswith(".ma") or p.endswith(".mb")


def _norm(path: str) -> str:
    return (path or "").strip().replace("\\", "/")


def extract_deps_from_ma(ma_path: str, *, include_string_paths: bool = True) -> List[str]:
    """
    Extract dependency paths from Maya ASCII.
    - references via 'file -r ... "path";'
    - optional: other quoted strings that look like file paths (textures/caches)
    """
    out: List[str] = []
    p = Path(ma_path)
    if not p.exists() or not p.is_file():
        return out

    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = _MA_REF_RE.match(line)
                if m:
                    out.append(_norm(m.group(1)))
                    continue

                if include_string_paths:
                    # Grab quoted strings and keep ones with known extensions
                    for s in _MA_STRING_PATH_RE.findall(line):
                        ss = _norm(s)
                        sl = ss.lower()
                        if any(sl.endswith(ext) for ext in _DEP_EXTS):
                            out.append(ss)
    except Exception:
        return []

    # stable dedupe (preserve order)
    seen: Set[str] = set()
    deduped: List[str] = []
    for x in out:
        k = x.lower()
        if k in seen:
            continue
        seen.add(k)
        deduped.append(x)
    return deduped


def extract_deps_from_mb_via_mayapy(mb_path: str, *, mayapy: str) -> List[str]:
    """
    Extract dependencies from Maya Binary using mayapy (best-effort).
    Requires mayapy available.
    """
    if not mayapy or not Path(mayapy).exists():
        return []

    p = Path(mb_path)
    if not p.exists() or not p.is_file():
        return []

    script = r"""
import json
import maya.standalone
maya.standalone.initialize(name="python")
import maya.cmds as cmds

path = r"%s"
out = {"refs": [], "textures": []}

cmds.file(new=True, force=True)
cmds.file(path, o=True, force=True, prompt=False, ignoreVersion=True)

try:
    out["refs"] = cmds.file(q=True, r=True) or []
except Exception:
    out["refs"] = []

tex = []
for n in (cmds.ls(type="file") or []):
    try:
        v = cmds.getAttr(n + ".fileTextureName")
        if v: tex.append(v)
    except Exception:
        pass

for n in (cmds.ls(type="aiImage") or []):
    try:
        v = cmds.getAttr(n + ".filename")
        if v: tex.append(v)
    except Exception:
        pass

out["textures"] = tex
print(json.dumps(out))
""" % (str(p).replace("\\", "\\\\"))

    try:
        proc = subprocess.run([mayapy, "-c", script], capture_output=True, text=True)
        if proc.returncode != 0:
            return []
        line = (proc.stdout or "").strip().splitlines()[-1]
        data = json.loads(line)
        out = (data.get("refs") or []) + (data.get("textures") or [])
    except Exception:
        return []

    # dedupe
    seen: Set[str] = set()
    deduped: List[str] = []
    for x in out:
        xx = _norm(str(x))
        k = xx.lower()
        if not xx or k in seen:
            continue
        seen.add(k)
        deduped.append(xx)
    return deduped


def discover_maya_dependencies(
    entry_file: str,
    *,
    mayapy: str = "",
    max_depth: int = 4,
    max_nodes: int = 2000,
) -> List[str]:
    """
    Returns a deduped list of dependency paths discovered from a Maya workfile.

    IMPORTANT: This function only *discovers paths*.
    Your download service should:
      - map path -> (remote_src, local_dst)
      - download
      - then optionally recurse into newly-downloaded maya deps
    """
    entry = _norm(entry_file)
    if not entry:
        return []

    # We do a shallow parse of the entry file; deeper recursion should be driven
    # by the download loop once deps exist locally.
    if entry.lower().endswith(".ma"):
        return extract_deps_from_ma(entry)
    if entry.lower().endswith(".mb"):
        return extract_deps_from_mb_via_mayapy(entry, mayapy=mayapy) if mayapy else []
    return []
