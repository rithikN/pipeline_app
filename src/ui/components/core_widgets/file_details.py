"""
file_details.py

Defines the FileDetailsWidget for displaying and managing details about a file,
including text-based metadata and an optional video preview.
"""

import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import Signal, QTimer, QSize

from ui.components.forms.preview_details_form import Ui_PreviewDetailsForm  # Generated UI
from ui.components.extensions.message_box import MessageBox
from ui.components.extensions.video_widget import VideoPlayer
from ui.utils.common import set_layout_visibility
from services.constants import VIDEO_PATH, SKIP_DATA

# Initialize logger
logger = logging.getLogger(__name__)


class FileDetailsWidget(QWidget):
    """
    A widget for displaying file details and optionally previewing a video.
    """

    # Signals for user actions (buttons)
    send_to_review_trigerred = Signal(dict)
    explorerRequested = Signal()
    launchRequested = Signal()
    publishRequested = Signal()

    def __init__(self, title: str, details_data: dict = None):
        """
        Initialize the FileDetailsWidget.

        Args:
            title (str): The title to display in the header_label.
            details_data (dict, optional): Initial file details data. Defaults to None.
        """
        super().__init__()
        logger.info("Initializing FileDetailsWidget.")

        self.details_data_to_be_shown = {}
        self._details_data = details_data or {}

        # Set up the UI
        self._ui = Ui_PreviewDetailsForm()
        self._ui.setupUi(self)

        self.message_box = MessageBox()

        # Configure UI fields
        self._ui.header_label.setText(title)
        self._ui.details_textEdit.setReadOnly(True)
        self._ui.details_textEdit.setViewportMargins(5, 0, 0, 10)

        # Hide layout until valid data is set
        set_layout_visibility(self._ui.main_horizontalLayout, False)

        # Set button icons
        self._ui.explorer_button.setIcon(QIcon("resources/icons/detail_form/explorer.svg"))
        self._ui.explorer_button.setIconSize(QSize(20, 20))
        self._ui.open_button.setIcon(QIcon("resources/icons/detail_form/open.svg"))
        self._ui.open_button.setIconSize(QSize(20, 20))

        # Wire buttons → signals
        self._setup_connections()

        # Initialize details if provided
        if self._details_data:
            self.details_data = self._details_data

    # --------------------------
    # UI Wiring
    # --------------------------
    def _setup_connections(self):
        """Connect UI buttons to intent signals."""
        logger.debug("Setting up connections for FileDetailsWidget.")
        self._ui.explorer_button.clicked.connect(self.explorerRequested.emit)
        self._ui.open_button.clicked.connect(self.launchRequested.emit)
        self._ui.upload_preview_button.clicked.connect(self.publishRequested.emit)

    # --------------------------
    # Public API
    # --------------------------
    @property
    def details_data(self) -> dict:
        """dict: The current file details data displayed by the widget."""
        return self._details_data

    @details_data.setter
    def details_data(self, task_data: dict):
        """Update the file details text area from task data."""
        if not isinstance(task_data, dict):
            raise ValueError("details_data must be a dictionary.")

        if not task_data:
            logger.debug("No details data provided; hiding main layout.")
            set_layout_visibility(self._ui.main_horizontalLayout, False)
            return

        logger.debug("Updating details data in FileDetailsWidget.")
        work_detail = task_data.get("work_detail")
        self._display_details(work_detail)
        set_layout_visibility(self._ui.main_horizontalLayout, True)
        self._clear_preview_frame()

        # If caller provides video_path directly, render it
        if task_data.get(VIDEO_PATH):
            QTimer.singleShot(
                50, lambda: self._initialize_video_player(task_data[VIDEO_PATH])
            )

    def set_preview(self, preview_path: str, resolution: str = None):
        """
        Update the preview display (video or image).
        """
        self._clear_preview_frame()

        if preview_path and Path(preview_path).exists():
            QTimer.singleShot(
                50, lambda: self._initialize_video_player(str(preview_path))
            )
        else:
            logger.debug("No preview file available")

    # --------------------------
    # Internal helpers
    # --------------------------
    def _initialize_video_player(self, video_path: str):
        """Initialize the video player if a video path is provided."""
        logger.debug(f"Initializing video player for path: {video_path}")
        self._video_player = VideoPlayer(video_path, self._ui.preview_frame)

    def _clear_preview_frame(self):
        """Remove all widgets/layouts from the preview_frame."""
        logger.debug("Clearing preview frame contents.")
        layout = self._ui.preview_frame.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            layout.deleteLater()

    def _display_details(self, details: dict):
        """Update text fields based on details dict."""
        if details:
            self.details_data_to_be_shown = {
                key: value for key, value in details.items() if key not in SKIP_DATA
            }
            self._details_data = details
            self._update_text_field()
            self._update_text_formatting()

    def _update_text_field(self):
        """Plain text formatting of details."""
        new_text = "\n".join(
            f"{key}: {value}" for key, value in self.details_data_to_be_shown.items()
        )
        self._ui.details_textEdit.setText(new_text)

    def _update_text_formatting(self):
        """Rich text (HTML) formatting of details."""
        html_content = "".join(
            f"<b>{key.upper()}</b>: {value}<br><hr>"
            for key, value in self._details_data.items()
        )
        html_content = html_content.rstrip("<hr>")
        self._ui.details_textEdit.setHtml(html_content)


# --------------------------
# Manual test harness
# --------------------------
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    widget = FileDetailsWidget("Testing")
    widget.show()

    # Example dynamic update after the widget is shown
    widget.details_data = {
        "File Name": "prj_e001_sq001_sh0001_dept_v001.ext",
        "File Type": "Maya / .ma",
        "File Size": "620.40 MB",
        "Last Saved": "01-02-2024 10:30",
        "Lock Status": "Unlocked",
        "local_preview_path": "progress_video2.mp4",
    }

    sys.exit(app.exec())
