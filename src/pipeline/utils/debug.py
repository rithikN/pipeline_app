"""
debug.py
Utility functions to help with debugging, tracing, and performance timing.
These are developer-oriented helpers, not meant for production logging.
"""

import time
import logging
from pathlib import Path
from inspect import currentframe, getframeinfo

logger = logging.getLogger(__name__)


def debug_tools(depth: int = 1) -> str:
    """
    Returns the filename, line number, and function name of the caller.

    Args:
        depth (int): How many frames to go back. Default=1 (immediate caller).

    Returns:
        str: A string like "file.py, line 42, in my_function"
    """
    frame = currentframe()
    # Step back `depth` frames
    for _ in range(depth):
        if frame and frame.f_back:
            frame = frame.f_back
    if not frame:
        return "Unknown location"

    dt = getframeinfo(frame)
    return f"{Path(dt.filename).name}, line {dt.lineno}, in {dt.function}"


def log_checkpoint(message: str = "Checkpoint", depth: int = 1):
    """
    Log a debug message with the caller's location for quick checkpoints.

    Args:
        message (str): Message to log alongside location.
        depth (int): Stack depth to walk back. Default=1.
    """
    location = debug_tools(depth + 1)
    logger.debug(f"{message} @ {location}")


class Timer:
    """
    Simple context manager to measure execution time of a block of code.

    Example:
        with Timer("Expensive operation"):
            do_something()
    """

    def __init__(self, label: str = "Block"):
        self.label = label
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        logger.debug(f"[TIMER START] {self.label}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (time.perf_counter() - self.start_time) * 1000  # ms
        logger.debug(f"[TIMER END] {self.label}: {elapsed:.2f} ms")
