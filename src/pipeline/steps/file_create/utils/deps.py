from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set


@dataclass(frozen=True)
class DependencyInput:
    kind: str
    path: str
    meta: Dict[str, Any]


def normalize_dependency_inputs(raw: Iterable[Any]) -> List[DependencyInput]:
    """
    Backward-compatible normalizer used by processes/refs.py.

    Expected raw item keys:
      - kind: str
      - path: str
      - meta: dict
    """
    out: List[DependencyInput] = []
    for item in (raw or []):
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind") or "").strip()
        path = str(item.get("path") or "").strip()
        meta = item.get("meta") or {}
        if not isinstance(meta, dict):
            meta = {}
        if not kind or not path:
            continue
        out.append(DependencyInput(kind=kind, path=path, meta=meta))
    return out


# -----------------------------
# Namespace + category helpers
# -----------------------------

def _dep_namespace(meta: Dict[str, Any], *, used: Optional[Set[str]] = None) -> str:
    """
    Namespace contract:
      - Prefer meta["namespace"] if provided
      - Else derive from meta (entity_name/asset_name) + occurrence_index padding if present
    Supports multi-occurrence suffixing: BLK_01, BLK_02 ...
    """
    used = used or set()

    ns = meta.get("namespace")
    if ns:
        base = str(ns).strip()
    else:
        base = str(meta.get("entity_name") or meta.get("asset_name") or meta.get("name") or "DEP").strip()

    occ_i = meta.get("occurrence_index")
    occ_total = meta.get("occurrence_total")

    if occ_i is not None and occ_total:
        try:
            i = int(occ_i)
            base = f"{base}_{i:02d}"
        except Exception:
            pass

    # ensure uniqueness in scene
    cand = base
    if cand not in used:
        used.add(cand)
        return cand

    n = 2
    while True:
        cand = f"{base}_{n:02d}"
        if cand not in used:
            used.add(cand)
            return cand
        n += 1


def _dep_category_key(meta: Dict[str, Any]) -> str:
    """
    Category key helper (for grouping / mapping):
      - Prefer asset_type or entity_subtype
    """
    v = meta.get("asset_type") or meta.get("entity_subtype") or meta.get("category") or ""
    return str(v).strip()