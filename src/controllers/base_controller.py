# controllers/base_controller.py
import logging
from contextlib import contextmanager
from typing import Optional

from pipeline.events import Event

logger = logging.getLogger(__name__)

class BaseController:
    """
    Base class for all controllers.
    Provides a context manager for wrapping operations with progress/success/error events.
    Supports both event_manager (GUI) and headless (CLI) modes.
    """

    def __init__(self, event_manager=None, headless: bool = False):
        self.event_manager = event_manager
        self.headless = headless
        self.active_workers = []

    @contextmanager
    def operation(self, title: str, message: str, payload: Optional[dict] = None):
        """Context manager for wrapping operations with structured events."""
        event = Event(type="progress", title=title, message=message, payload=payload)

        if self.event_manager and not self.headless:
            self.event_manager.progressStarted.emit(event)
        else:
            logger.info(f"[START] {title}: {message}")

        try:
            yield
        except Exception as e:
            error_event = Event(type="error", title=title, message=str(e), payload=payload)
            if self.event_manager and not self.headless:
                self.event_manager.errorOccurred.emit(error_event)
            else:
                logger.error(f"[ERROR] {title}: {e}")
            raise
        else:
            success_event = Event(type="success", title=title, message="Operation completed", payload=payload)
            if self.event_manager and not self.headless:
                self.event_manager.progressFinished.emit(success_event)
            else:
                logger.info(f"[SUCCESS] {title}")

    def publish_event(self, signal_name: str, event: Event):
        """
        Publish a structured event in both GUI and headless modes.
        - In GUI mode: emit via event_manager.<signal_name>
        - In headless mode: log it.
        """
        if self.event_manager and not self.headless:
            signal = getattr(self.event_manager, signal_name, None)
            if signal:
                signal.emit(event)
            else:
                logger.warning(f"No signal named {signal_name} found in event_manager")
        else:
            logger.info(f"[{event.type.upper()}] {event.title}: {event.message}")


    def has_active_process(self) -> bool:
        """Return True if any job is still running."""
        return len(self.active_workers) > 0

    def add_worker(self, worker):
        self.active_workers.append(worker)

    def remove_worker(self, worker):
        if worker in self.active_workers:
            self.active_workers.remove(worker)
