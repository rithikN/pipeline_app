"""
file_details.py

Defines the FileDetailsWidget for displaying and managing details about a file,
including text-based metadata and an optional video preview.
"""

import logging

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Signal, QTimer, QSize

from ui.components.forms.details_form import Ui_DetailsForm  # Generated UI
from ui.components.extensions.message_box import MessageBox
from ui.components.extensions.video_widget import VideoPlayer
from ui.utils.common import set_layout_visibility
from services.constants import VIDEO_PATH

# Initialize logger
logger = logging.getLogger(__name__)


class FileDetailsWidget(QWidget):
    """
    A widget for displaying file details and optionally previewing a video.
    """

    # Signal to allow external components to trigger updates
    trigger_update = Signal(dict)

    def __init__(self, title: str, details_data: dict = None):
        """
        Initialize the FileDetailsWidget.

        Args:
            title (str): The title to display in the header_label.
            details_data (dict, optional): Initial file details data. Defaults to None.
        """
        super().__init__()
        logger.info("Initializing FileDetailsWidget.")

        # Set up the UI
        self._ui = Ui_DetailsForm()
        self._ui.setupUi(self)

        self.message_box = MessageBox()
        self._details_data = details_data if details_data else {}

        # Set up the UI labels/fields
        self._ui.header_label.setText(title)
        self._ui.details_textEdit.setReadOnly(True)
        self._ui.details_textEdit.setViewportMargins(5, 0, 0, 10)

        # Update text field based on initial details_data
        self._update_text_field()

        # Hide main layout by default until valid details_data is set
        set_layout_visibility(self._ui.main_horizontalLayout, False)

        # Connect UI buttons
        self._setup_connections()

    def _setup_connections(self):
        """
        Connect UI buttons to their respective handlers.
        """
        logger.debug("Setting up connections for FileDetailsWidget.")

        self._ui.delete_button.clicked.connect(
            lambda: self.message_box.show_message(
                "Yet To Implement",
                message_type="info",
                title="Delete"
            )
        )
        self._ui.explorer_button.clicked.connect(
            lambda: self.message_box.show_message(
                "Yet To Implement",
                message_type="info",
                title="Explorer"
            )
        )
        self._ui.open_button.clicked.connect(
            lambda: self.message_box.show_message(
                "Yet To Implement",
                message_type="info",
                title="Open"
            )
        )

    @property
    def details_data(self) -> dict:
        """
        dict: The current file details data displayed by the widget.
        """
        return self._details_data

    @details_data.setter
    def details_data(self, data: dict):
        """
        Set or update the file details data, re-initializing the UI if necessary.

        Args:
            data (dict): New details data to display.
        """
        if not isinstance(data, dict):
            raise ValueError("details_data must be a dictionary.")

        if not data:
            logger.debug("No details data provided; hiding main layout.")
            set_layout_visibility(self._ui.main_horizontalLayout, False)
            return

        logger.debug(f"Updating details data: {data}")
        self._update_details(data)
        set_layout_visibility(self._ui.main_horizontalLayout, True)

        # Clear any existing preview widgets
        self._clear_preview_frame()

        # If there's a video path, initialize the video player (slightly delayed)
        if data.get(VIDEO_PATH):
            QTimer.singleShot(50, lambda: self._initialize_video_player(data[VIDEO_PATH]))
        else:
            logger.debug(f"No video path ({VIDEO_PATH}) provided.")

    def _initialize_video_player(self, video_path: str):
        """
        Initialize the video player if a video path is provided.

        Args:
            video_path (str): Path to the video file.
        """
        logger.debug(f"Initializing video player for path: {video_path}")
        self._video_player = VideoPlayer(video_path, self._ui.preview_frame)

    def _clear_preview_frame(self):
        """
        Remove all widgets/layouts from the preview_frame.
        """
        logger.debug("Clearing preview frame contents.")
        layout = self._ui.preview_frame.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.setParent(None)
            layout.deleteLater()

    def _update_details(self, details: dict):
        """
        Update the internal details data and text field.

        Args:
            details (dict): New details to be displayed.
        """
        self._details_data = details
        self._update_text_field()

    def _update_text_field(self):
        """
        Construct a display string from _details_data and set it in the details_textEdit.
        """
        new_text = "\n".join(
            f"{key}: {value}" for key, value in self._details_data.items()
        )
        self._ui.details_textEdit.setText(new_text)


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
        "preview_path": "C:/Users/sknay/Videos/progress_video2.mp4"
    }

    sys.exit(app.exec())
