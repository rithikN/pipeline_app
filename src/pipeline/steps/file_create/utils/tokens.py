from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Mapping, Optional, Set, Tuple

TOKEN_RE = re.compile(r"\$\{([A-Z0-9_]+)\}")


@dataclass
class TokenError(ValueError):
    token: str
    reason: str


def extract_tokens(s: str) -> Set[str]:
    return set(TOKEN_RE.findall(s or ""))


def resolve_template(
    s: str,
    tokens: Mapping[str, Any],
    *,
    strict: bool = False,
    validators: Optional[Dict[str, Callable[[str], bool]]] = None,
) -> str:
    validators = validators or {}

    needed = extract_tokens(s)
    if strict:
        for t in needed:
            if t not in tokens or tokens[t] in (None, ""):
                raise TokenError(t, "missing")
            v = str(tokens[t])
            if t in validators and not validators[t](v):
                raise TokenError(t, "invalid '%s'" % v)

    def repl(m):
        key = m.group(1)
        if key not in tokens:
            return m.group(0)  # keep placeholder if unknown
        v = "" if tokens[key] is None else str(tokens[key])
        if strict and key in validators and v and not validators[key](v):
            raise TokenError(key, "invalid '%s'" % v)
        return v

    return TOKEN_RE.sub(repl, s or "")


def resolve_tokens(obj: Any, tokens: Mapping[str, Any]) -> Any:
    """
    Deep token resolver for JSON-like objects (dict/list/tuple/str).
    Missing tokens keep placeholders unchanged (non-strict).
    """
    if obj is None:
        return None
    if isinstance(obj, str):
        return resolve_template(obj, tokens, strict=False)
    if isinstance(obj, list):
        return [resolve_tokens(x, tokens) for x in obj]
    if isinstance(obj, tuple):
        return tuple(resolve_tokens(x, tokens) for x in obj)
    if isinstance(obj, dict):
        return {k: resolve_tokens(v, tokens) for k, v in obj.items()}
    return obj


def ctx_tokens(ctx: Any) -> Tuple[Dict[str, Any], List[str]]:
    """
    Preferred source of truth: backend token dict in payload under ctx['tokens'].

    Backward compatibility:
      - If ctx['tokens'] is missing, we derive a minimal legacy set from ctx keys
        to avoid breaking old payloads, but we return a warning.
      - We do NOT "fix" token values; we only mirror what payload already has.
    """
    warns: List[str] = []

    raw = ctx.get("tokens", None)
    toks: Dict[str, Any] = {}
    if isinstance(raw, dict):
        toks.update(raw)

    if toks:
        return toks, warns

    # Legacy fallback (only if backend tokens not provided)
    warns.append("[file_create] payload missing 'tokens' dict; using legacy derived tokens for templates")

    def _get(*keys: str) -> str:
        for k in keys:
            v = ctx.get(k, None)
            if v not in (None, ""):
                return str(v)
        return ""

    toks.update(
        {
            "ASSET_NAME": _get("asset_name", "entity_name"),
            "SHOT_NAME": _get("shot", "entity_name"),
            "ENTITY_NAME": _get("entity_name"),
            "TASK": _get("task").upper(),
            "DEPARTMENT": _get("department").upper(),
            "SUBTYPE": _get("entity_subtype").upper(),
            "SUBTYPE_CODE": _get("entity_subtype_code"),
            "EPISODE": _get("episode"),
            "SEQUENCE": _get("sequence"),
        }
    )
    return toks, warns