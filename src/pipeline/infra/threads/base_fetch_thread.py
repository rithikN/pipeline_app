# pipeline/infra/threads/base_fetch_thread.py
import logging
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)


class BaseFetchThread(QThread):
    """
    Abstract base for data fetching threads.
    Provides signals + safe emit/error wrappers.
    """

    data_fetched = Signal(object)  # result type flexible: list, dict, tuple
    error_occurred = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args
        self.kwargs = kwargs

    def safe_emit(self, result):
        """Emit result safely with debug logging."""
        logger.debug("%s: emitting result", self.__class__.__name__)
        self.data_fetched.emit(result)

    def safe_error(self, error: Exception):
        """Emit error safely with debug logging."""
        logger.error("%s: %s", self.__class__.__name__, error, exc_info=True)
        self.error_occurred.emit(str(error))

    def run(self):
        raise NotImplementedError("Subclasses must implement run()")
