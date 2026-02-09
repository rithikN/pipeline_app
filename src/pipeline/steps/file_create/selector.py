from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


def _case_insensitive_get(d: Dict[str, Any], key: str) -> Optional[Any]:
    if key in d:
        return d[key]
    k2 = (key or "").strip().lower()
    if not k2:
        return None
    for kk, vv in d.items():
        if str(kk).strip().lower() == k2:
            return vv
    return None

# ToDo Need Test here
def _select_process_block(cfg: Dict[str, Any], payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Backward compatible selection:
      - If cfg has top-level "processes": use it (old format)
      - Else use hierarchical format:
          shot: cfg["shot_pipeline"][DEPT]
          asset: cfg["asset_pipeline"][ENTITY_SUBTYPE][DEPT]

    FINAL PAYLOAD KEYS ONLY:
      - entity_type
      - department
      - entity_subtype
    """
    if isinstance(cfg.get("processes"), list):
        return cfg, list(cfg.get("processes") or [])

    entity_type = str(payload.get("entity_type") or "").strip().lower()
    dept = str(payload.get("department") or "").strip()
    if not entity_type or not dept:
        return {}, []

    if entity_type == "shot":
        shot_pipe = cfg.get("shot_pipeline", {}) or {}
        block = _case_insensitive_get(shot_pipe, dept)
        if not isinstance(block, dict):
            raise KeyError(f"No shot_pipeline config for department={dept}")
        return block, list(block.get("processes") or [])

    if entity_type != "asset":
        raise KeyError(f"Unknown entity_type={entity_type!r} (expected 'asset' or 'shot')")

    asset_pipe = cfg.get("asset_pipeline", {}) or {}
    asset_cat = str(payload.get("entity_subtype") or "").strip()
    if not asset_cat:
        raise KeyError("Asset pipeline requires payload key entity_subtype (e.g. Characters/Props)")

    cat_block = _case_insensitive_get(asset_pipe, asset_cat)
    if not isinstance(cat_block, dict):
        raise KeyError(f"No asset_pipeline config for entity_subtype={asset_cat}")

    dept_block = _case_insensitive_get(cat_block, dept)
    if not isinstance(dept_block, dict):
        raise KeyError(f"No asset_pipeline config for entity_subtype={asset_cat}, department={dept}")

    return dept_block, list(dept_block.get("processes") or [])


def select_processes(cfg: Dict[str, Any], payload: Dict[str, Any]) -> List[str]:
    """
    Returns ordered list of process names to run.
    """
    _block, processes = _select_process_block(cfg, payload)
    return list(processes or [])