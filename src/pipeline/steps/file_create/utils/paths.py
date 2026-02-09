from __future__ import annotations

import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike]


def norm_maya_path(p: PathLike) -> str:
    """
    Normalize a filesystem path for Maya:
      - accepts Windows paths
      - converts backslashes to forward slashes
      - preserves drive letter
    """
    s = str(p)
    s = s.replace("\\", "/")
    # Collapse accidental double slashes (but keep //server/share style)
    if not s.startswith("//"):
        while "//" in s:
            s = s.replace("//", "/")
    return s


def ensure_parent_dir(path: PathLike) -> None:
    Path(str(path)).parent.mkdir(parents=True, exist_ok=True)