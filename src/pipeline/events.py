# events.py
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Event:
    type: str            # e.g., "progress", "success", "error"
    title: str
    message: str
    payload: Optional[Any] = None
