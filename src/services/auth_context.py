# services/auth_context.py
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Optional


@dataclass
class AuthTokens:
    access: Optional[str] = None
    refresh: Optional[str] = None


_LOCK = RLock()
_TOKENS = AuthTokens()


def set_tokens(access: str | None, refresh: str | None = None) -> None:
    """Store tokens in-memory for this app session."""
    with _LOCK:
        _TOKENS.access = access
        if refresh is not None:
            _TOKENS.refresh = refresh


def clear_tokens() -> None:
    with _LOCK:
        _TOKENS.access = None
        _TOKENS.refresh = None


def get_access_token() -> Optional[str]:
    with _LOCK:
        return _TOKENS.access


def get_refresh_token() -> Optional[str]:
    with _LOCK:
        return _TOKENS.refresh

