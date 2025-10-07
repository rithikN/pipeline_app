# signal_manager.py

from PySide6.QtCore import QObject, Signal
import logging
from pipeline.events import Event

logger = logging.getLogger(__name__)


class SignalManager(QObject):
    """
    Centralized manager for handling signals across the application.
    All cross-application signals are declared here.
    """

    # Core application signals
    update_triggered       = Signal()
    exit_triggered         = Signal()
    wiki_triggered         = Signal()
    about_triggered        = Signal()
    edit_triggered         = Signal()
    logout_triggered       = Signal()
    download_triggered     = Signal()
    exit_project_triggered = Signal()
    refresh_triggered      = Signal()

    # Structured event signals (controllers → UI/CLI)
    progressStarted  = Signal(Event)   # when a long operation starts
    progressFinished = Signal(Event)   # when a long operation ends
    errorOccurred    = Signal(Event)   # when an error is raised
    taskUpdated      = Signal(Event)   # when a task is updated
    fileVersioned    = Signal(Event)   # when a file version changes
    projectSynced    = Signal(Event)   # when a project sync completes
    fileCreated      = Signal(Event)   # when a file created
    fileOpened    = Signal(Event)
    fileClosed    = Signal(Event)
    fileVersioned = Signal(Event)
    filePublished = Signal(Event)
    assetListReady    = Signal(Event)
    assetTrackerError = Signal(Event)
    assetTrackerEmpty = Signal(Event)

    def __init__(self):
        super().__init__()
        logger.debug("SignalManager initialized with predefined signals.")


    def emit_error(self, msg: str):
        self.errorOccurred.emit(msg)
