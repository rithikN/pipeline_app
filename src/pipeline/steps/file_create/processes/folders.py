from __future__ import annotations

import os
from typing import Any, List

from .registry import process


@process("makeFolders")
def makeFolders(ctx: Any) -> None:
    """
    FINAL CONTRACT (matches legacy):
      - ctx["sub_folders"]: List[str]
    """
    folders: List[str] = list(ctx.get("sub_folders") or [])
    if not folders:
        print("[makeFolders] ERROR: payload missing 'sub_folders' or it is empty")
        return

    for p in folders:
        os.makedirs(p, exist_ok=True)
        print(f"[make sub-folders] {p}")