from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class PipelineProcessError(RuntimeError):
    """
    Wraps exceptions thrown by a process with structured context.

    This is intentionally lightweight (stdlib only) and safe to raise across
    both mayapy and normal python.
    """
    process_name: str
    context: Dict[str, Any]
    original: BaseException

    def __str__(self) -> str:
        bits = []
        for k in ("project", "entity_type", "entity_name", "department", "task"):
            v = self.context.get(k)
            if v:
                bits.append(f"{k}={v}")
        ctx = ", ".join(bits) if bits else "no_ctx"
        return f"[file_create] process={self.process_name} ({ctx}): {self.original}"