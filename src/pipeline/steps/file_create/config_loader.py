from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from .utils.jsonutil import deep_merge, safe_read_json
from .utils.tokens import resolve_template  # <-- use your new resolver


def _config_root() -> Path:
    # resolve() avoids cwd surprises
    return Path(__file__).resolve().parent / "config"


def load_project_config(project: str) -> Dict[str, Any]:
    root = _config_root()
    base_path = root / "base.json"
    proj_path = root / "projects" / f"{project}.json"

    base = safe_read_json(str(base_path)) or {}
    proj = safe_read_json(str(proj_path)) or {}

    if not proj:
        raise FileNotFoundError(f"Project config not found: {proj_path}")

    return deep_merge(base, proj)


def load_group_templates(project: Optional[str] = None, cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Priority:
      1) inline in project cfg: cfg["group_templates"]
      2) project-specific file: config/projects/<PROJECT>/group_templates.json
      3) project-specific alt:  config/projects/<PROJECT>_group_templates.json
      4) global fallback:       config/group_templates.json (or groups.json / group.json)
    """
    root = _config_root()

    if cfg and isinstance(cfg.get("group_templates"), dict):
        return cfg["group_templates"]

    candidates = []
    if project:
        candidates += [
            root / "projects" / project / "group_templates.json",
            root / "projects" / f"{project}_group_templates.json",
        ]

    candidates += [
        root / "group_templates.json",
        root / "groups.json",
        root / "group.json",
    ]

    for p in candidates:
        data = safe_read_json(str(p))
        if data:
            return data

    return {}


def resolve_config_tokens(cfg: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optional: expand ${TOKENS} inside config using backend tokens only.
    """
    toks = payload.get("tokens")
    if not isinstance(toks, dict) or not toks:
        return cfg

    def _walk(o: Any) -> Any:
        if isinstance(o, dict):
            return {k: _walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_walk(x) for x in o]
        if isinstance(o, str):
            return resolve_template(o, toks, strict=False)
        return o

    return _walk(cfg)