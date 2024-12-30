# signal_manager.py

from PySide6.QtCore import QObject, Signal
import logging

logger = logging.getLogger(__name__)


class SignalManager(QObject):
    """
    Centralized manager for handling signals across the application.
    All signals are predefined as class attributes.
    """

    # Predefined signals
    update_triggered = Signal()
    exit_triggered = Signal()
    wiki_triggered = Signal()
    about_triggered = Signal()
    edit_triggered = Signal()
    logout_triggered = Signal()
    download_triggered = Signal()
    exit_project_triggered = Signal()

    def __init__(self):
        super().__init__()
        logger.debug("SignalManager initialized with predefined signals.")
