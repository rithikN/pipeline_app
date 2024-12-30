"""
task_details.py

Defines the TaskDetailsWidget, which displays task details and logs,
along with an optional image preview (maintaining a 16:9 aspect ratio).
"""

import logging
from typing import Optional, Dict, List

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPixmap, QPainter

from ui.components.forms.task_details_form import Ui_TaskDetailsForm
from ui.components.core_widgets.task_log import TaskLogWidget
from ui.components.extensions.message_box import MessageBox
from ui.utils.common import set_layout_visibility

from services.constants import PREVIEW_PATH

# Initialize logger (optional)
logger = logging.getLogger(__name__)


class TaskDetailsWidget(QWidget):
    """
    A widget that displays task details (metadata), task logs, and a preview image.
    """

    # Signal to allow external components to trigger updates
    trigger_update = Signal(dict)

    def __init__(
            self,
            title: str,
            task_details_data: Optional[Dict] = None,
            task_logs_data: Optional[List] = None,
            parent: Optional[QWidget] = None
    ):
        """
        Initialize the TaskDetailsWidget.

        Args:
            title (str): The header label text.
            task_details_data (dict, optional): Dictionary of task details. Defaults to None.
            task_logs_data (list, optional): List of task logs. Defaults to None.
            parent (QWidget, optional): The parent widget, if any. Defaults to None.
        """
        super().__init__(parent)
        logger.debug("Initializing TaskDetailsWidget.")

        self.message_box = MessageBox()

        # Instantiate and set up the UI
        self._ui = Ui_TaskDetailsForm()
        self._ui.setupUi(self)

        # Internal state
        self._task_logs_data = task_logs_data if task_logs_data else []
        self._task_details_data = task_details_data if task_details_data else {}

        self.header_label = self._ui.header_label
        self.task_details_textEdit = self._ui.task_details_textEdit
        self.taskLog_frame = self._ui.taskLog_frame
        self.preview_frame = self._ui.preview_frame
        self.task_details_textEdit = self._ui.task_details_textEdit

        # Additional UI setup
        self._setup_ui(title)

        # Connect the update signal
        self.trigger_update.connect(self._on_trigger_update)

    def _setup_ui(self, title: str):
        """
        Configure the UI elements, integrate the TaskLogWidget,
        and set up the preview image.
        """
        logger.debug("Setting up UI for TaskDetailsWidget.")
        self.header_label.setText(title)
        self.header_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.header_label.setMinimumHeight(38)
        self.header_label.setMaximumHeight(38)

        # Make the textEdit read-only for task details
        self.task_details_textEdit.setReadOnly(True)
        self.task_details_textEdit.setViewportMargins(5, 0, 0, 10)

        # Update the text from the current details
        self._update_details_text()

        # Initialize the TaskLogWidget
        self._task_log_widget = TaskLogWidget()
        self._task_log_widget.set_tasks_data(self._task_logs_data)

        # Embed the TaskLogWidget into the taskLog_frame
        task_log_layout = QVBoxLayout(self.taskLog_frame)
        task_log_layout.setContentsMargins(0, 0, 0, 0)
        task_log_layout.setSpacing(0)
        task_log_layout.addWidget(self._task_log_widget)

        # Initialize the image label for previews
        self._image_label = QLabel()
        self._image_label.setScaledContents(True)

        # Ensure the preview_frame has a layout
        if not self.preview_frame.layout():
            self.preview_frame.setLayout(QVBoxLayout())
        self.preview_frame.layout().addWidget(self._image_label)

        # Display the preview image if applicable
        preview_path = self._task_details_data.get(PREVIEW_PATH)
        self._set_preview_image(preview_path)

        # Hide main layout if no details are provided
        set_layout_visibility(self._ui.verticalLayout_3, bool(self._task_details_data))
        self._ui.open_button.clicked.connect(
            lambda: self.message_box.show_message(
                "Yet To Implement",
                message_type="info",
                title="Open in Kitsu"
            )
        )

    def _update_details_text(self):
        """
        Construct and set the task details text in task_details_textEdit.
        """
        if self._task_details_data:
            new_text = "\n".join(
                f"{key}: {value}" for key, value in self._task_details_data.items() if key != PREVIEW_PATH
            )
            self.task_details_textEdit.setText(new_text)
        else:
            self.task_details_textEdit.clear()

    def _set_preview_image(self, image_path: Optional[str] = None):
        """
        Create a placeholder (16:9) pixmap or load/scale an external image,
        then display it in the preview label.

        Args:
            image_path (str, optional): Path to the image file.
        """
        logger.debug(f"Setting preview image from path: {image_path}")
        placeholder_width = 195
        placeholder_height = 110

        # Create a placeholder pixmap
        placeholder_pixmap = QPixmap(placeholder_width, placeholder_height)
        placeholder_pixmap.fill(Qt.lightGray)

        if not image_path:
            return
        # Load the external image
        external_pixmap = QPixmap(image_path)

        if not external_pixmap.isNull():  # Check if the image is loaded successfully
            # Scale the external image to fit within the placeholder while maintaining aspect ratio
            scaled_pixmap = external_pixmap.scaled(
                placeholder_width, placeholder_height,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            # Center the scaled image onto the placeholder using QPainter
            painter = QPainter(placeholder_pixmap)
            x_offset = (placeholder_width - scaled_pixmap.width()) // 2
            y_offset = (placeholder_height - scaled_pixmap.height()) // 2
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
            painter.end()

        self._image_label.setPixmap(placeholder_pixmap)

    def _on_trigger_update(self, data: dict):
        """
        Slot to handle the trigger_update signal for updating content externally.
        """
        logger.debug(f"Received trigger_update signal with data: {data}")
        if "details_data" in data:
            self.details_data = data["details_data"]
        if "task_logs" in data:
            self.task_logs = data["task_logs"]

    # ---------------------------
    # Public Properties & Setters
    # ---------------------------

    @property
    def details_data(self) -> dict:
        """Get the task details dictionary."""
        return self._task_details_data

    @details_data.setter
    def details_data(self, data: dict):
        """
        Set new task details data and update the UI.

        Args:
            data (dict): Dictionary containing key-value pairs for task details.
        """
        logger.debug(f"Setting details_data: {data}")
        if not isinstance(data, dict):
            raise ValueError("details_data must be a dictionary")

        self._task_details_data = data
        set_layout_visibility(self._ui.verticalLayout_3, bool(data))
        self._update_details_text()
        self._set_preview_image(data.get("preview_path"))

    @property
    def task_logs(self) -> list:
        """Get the current list of task logs."""
        return self._task_logs_data

    @task_logs.setter
    def task_logs(self, logs: list):
        """
        Set a new list of task logs and update the TaskLogWidget.

        Args:
            logs (list): A list of task log dictionaries.
        """
        logger.debug(f"Setting task_logs: {logs}")
        if not isinstance(logs, list):
            raise ValueError("task_logs must be a list", logs)

        self._task_logs_data = logs
        self._task_log_widget.set_tasks_data(logs)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    # Configure logging for standalone testing
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)

    # Example details
    task_details = {
        "File Name": "prj_e001_sq001_sh0001_dept_v001.ext",
        "File Type": "Maya / .ma",
        "File Size": "620.40 MB",
        "Last Saved": "01-02-2024 10:30",
        "preview_path": "path/to/preview_image.png",
    }
    task_logs = [
        {"task_status": "APPROVED", "username": "John Doe", "date": "01-15 10:30", "comment": "Reviewed and approved."},
        {"task_status": "IN PROGRESS", "username": "Jane Smith", "date": "01-12 14:00", "comment": "Work in progress."},
    ]

    widget = TaskDetailsWidget("Task Details", task_details, task_logs)
    widget.show()

    # Example dynamic update
    widget.details_data = {
        "File Name": "prj_e002_sq002_sh0002_dept_v002.ext",
        "File Type": "Blender / .blend",
        "File Size": "1.2 GB",
        "Last Saved": "02-05-2024 15:45",
        "Lock Status": "Locked",
        "preview_path": "path/to/new_preview_image.png",
    }

    widget.task_logs = [
        {"task_status": "REVIEW", "username": "Michael Brown", "date": "02-10 11:20", "comment": "Needs revision.",
         "task_status_color": "blue"},
        {"task_status": "DONE", "username": "Emily White", "date": "02-11 16:00",
         "comment": "Finalized and ready for submission.", "task_status_color": "green"},
    ]

    # Trigger an update via the signal
    widget.trigger_update.emit({
        "details_data": {
            "File Name": "prj_e003_sq003_sh0003_dept_v003.ext",
            "File Type": "Nuke / .nk",
            "File Size": "2.3 GB",
            "Last Saved": "03-01-2024 12:00",
            "Lock Status": "Unlocked",
            "preview_path": "path/to/another_preview_image.png",
        },
        "task_logs": [
            {"task_status": "PENDING", "username": "Alice Green", "date": "03-02 10:00", "comment": "Pending review.",
             "task_status_color": "orange"},
        ],
    })

    sys.exit(app.exec())
