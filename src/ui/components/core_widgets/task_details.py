"""
task_details.py

Defines the TaskDetailsWidget, which displays task details and logs,
along with an optional image preview (maintaining a 16:9 aspect ratio).
"""

import logging
from typing import Optional, Dict, List

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QFrame
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QIcon

from ui.components.forms.task_details_form import Ui_TaskDetailsForm
from ui.components.core_widgets.task_log import TaskLogWidget
from ui.components.extensions.message_box import MessageBox
from ui.utils.common import set_layout_visibility

from services.constants import PREVIEW_PATH

# Initialize logger
logger = logging.getLogger(__name__)


class TaskDetailsWidget(QWidget):
    """
    Widget for displaying task details (metadata), task logs, and a preview image.
    """

    trigger_update = Signal(dict)  # Allows external updates via emitted data

    def __init__(
        self,
        title: str,
        task_details_data: Optional[Dict] = None,
        task_logs_data: Optional[List] = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        logger.debug("Initializing TaskDetailsWidget.")

        # Dependencies
        self.message_box = MessageBox() # ToDo plug global message_box or remove if not needed

        # Setup UI
        self._ui = Ui_TaskDetailsForm()
        self._ui.setupUi(self)

        # Internal state
        self._task_details_data: Dict = task_details_data or {}
        self._task_logs_data: List = task_logs_data or []

        # UI setup
        self._setup_ui(title)

        # Signal connections
        self.trigger_update.connect(self._on_trigger_update)

    # ---------------------------
    # UI Setup
    # ---------------------------

    def _setup_ui(self, title: str):
        """Configure UI elements, integrate TaskLogWidget, and setup preview."""
        logger.debug("Setting up UI for TaskDetailsWidget.")

        # Header
        self._ui.header_label.setText(title)
        self._ui.header_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._ui.header_label.setFixedHeight(38)

        # Task details textEdit
        self._ui.task_details_textEdit.setReadOnly(True)
        self._ui.task_details_textEdit.setViewportMargins(5, 0, 0, 10)

        # Fill initial details
        self._update_details_text()

        # Task log widget
        self._task_log_widget = TaskLogWidget()
        self._task_log_widget.set_tasks_data(self._task_logs_data)

        task_log_layout = QVBoxLayout(self._ui.taskLog_frame)
        task_log_layout.setContentsMargins(0, 0, 0, 0)
        task_log_layout.setSpacing(0)
        task_log_layout.addWidget(self._task_log_widget)

        # Preview image
        self._image_label = QLabel()
        self._image_label.setScaledContents(True)

        if not self._ui.preview_frame.layout():
            self._ui.preview_frame.setLayout(QVBoxLayout())

        self._ui.preview_frame.layout().addWidget(self._image_label)
        self._set_preview_image(self._task_details_data.get(PREVIEW_PATH))

        # Show/hide main layout depending on data
        set_layout_visibility(self._ui.verticalLayout_3, bool(self._task_details_data))

        # Open button
        self._ui.open_button.setIcon(QIcon("resources/icons/task_detail/open_in_kitsu.svg"))
        self._ui.open_button.setIconSize(QSize(20, 20))
        self._ui.open_button.clicked.connect(
            lambda: self.message_box.show_message(
                "Yet To Implement", message_type="info", title="Open in Kitsu"
            )
        )

    # ---------------------------
    # Internal Helpers
    # ---------------------------

    def _update_details_text(self):
        """Update task details text field with metadata."""
        if self._task_details_data:
            details_text = "\n".join(
                f"{key}: {value}" for key, value in self._task_details_data.items() if key != PREVIEW_PATH
            )
            self._ui.task_details_textEdit.setText(details_text)
        else:
            self._ui.task_details_textEdit.clear()

    def _set_preview_image(self, image_path: Optional[str]):
        """
        Load preview image or placeholder (16:9 gray box).
        """
        logger.debug(f"Setting preview image from: {image_path}")

        placeholder_size = QSize(195, 110)
        pixmap = QPixmap(placeholder_size)
        pixmap.fill(Qt.lightGray)

        if image_path:
            external_pixmap = QPixmap(image_path)
            if not external_pixmap.isNull():
                scaled = external_pixmap.scaled(
                    placeholder_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                painter = QPainter(pixmap)
                x_offset = (placeholder_size.width() - scaled.width()) // 2
                y_offset = (placeholder_size.height() - scaled.height()) // 2
                painter.drawPixmap(x_offset, y_offset, scaled)
                painter.end()

        self._image_label.setPixmap(pixmap)

    def _on_trigger_update(self, data: dict):
        """Handle trigger_update signal with new data."""
        logger.debug(f"Received trigger_update: {data}")
        if "details_data" in data:
            self.details_data = data["details_data"]
        if "task_logs" in data:
            self.task_logs = data["task_logs"]

    # ---------------------------
    # Public Properties
    # ---------------------------

    @property
    def details_data(self) -> Dict:
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
        logger.debug(f"Updating task_logs: {logs}")
        if not isinstance(logs, list):
            raise ValueError("task_logs must be a list", logs)

        self._task_logs_data = logs
        self._task_log_widget.set_tasks_data(logs)


# ---------------------------
# Standalone Testing
# ---------------------------
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
        {"status": "APPROVED", "username": "John Doe", "date": "01-15 10:30", "comment": "Reviewed and approved."},
        {"status": "IN PROGRESS", "username": "Jane Smith", "date": "01-12 14:00", "comment": "Work in progress."},
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
        {"status": "REVIEW", "username": "Michael Brown", "date": "02-10 11:20", "comment": "Needs revision.",
         "task_status_color": "blue"},
        {"status": "DONE", "username": "Emily White", "date": "02-11 16:00",
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
            {"status": "PENDING", "username": "Alice Green", "date": "03-02 10:00", "comment": "Pending review.",
             "task_status_color": "orange"},
        ],
    })

    sys.exit(app.exec())
