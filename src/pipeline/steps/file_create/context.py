from __future__ import annotations

from typing import Any, Dict, Optional


class Context:
    """
    Backward compatible context wrapper.

    Contract:
      - ctx.get(key, default=None)
      - ctx.set(key, value)
      - ctx.require(*keys)
      - ctx.__getattr__ falls back to ctx.get(name)

    NOTE:
      - get() falls back to config (legacy behavior).
      - require() treats falsy as missing (legacy behavior).
    """

    def __init__(self, payload: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> None:
        self._data: Dict[str, Any] = dict(payload or {})
        self._config: Dict[str, Any] = dict(config or {})

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._data:
            return self._data.get(key, default)
        if key in self._config:
            return self._config.get(key, default)
        return default

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def require(self, *keys: str) -> None:
        missing = [k for k in keys if not self.get(k, None)]
        if missing:
            raise KeyError(f"Missing required Context keys: {', '.join(missing)}")

    def __getattr__(self, name: str) -> Any:
        try:
            return self.get(name)
        except Exception as e:
            raise AttributeError(name) from e

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

    @property
    def config(self) -> Dict[str, Any]:
        return self._config