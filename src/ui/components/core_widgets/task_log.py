"""
task_log_widget.py

Provides a main window (MainWindow) that showcases a TaskLogWidget
for displaying logs related to tasks (e.g., status, username, date, comment).
"""

import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt, QSize

from services.constants import default_task_status_color, TASK_STATUS, USERNAME, DATE, COMMENT, STATUS_COLOR

logger = logging.getLogger(__name__)


class TaskContent(QWidget):
    """
    A widget for displaying the content of a single task log.

    Attributes:
        task_status (str): The status of the task (e.g., "APPROVED", "REVIEW").
        username (str): The username of the person associated with this task log.
        date (str): The date/time string for the log entry.
        comment (str): A short description or comment of this task log.
        task_status_color (str): A color hex string for styling the status label.
    """

    def __init__(
            self,
            task_status: str,
            username: str,
            date: str,
            comment: str,
            task_status_color: str = None,
            parent: QWidget = None
    ):
        """
        Initialize the TaskContent widget.

        Args:
            task_status (str): The status of the task.
            username (str): The username associated with this log.
            date (str): The date/time for the log.
            comment (str): The comment text.
            task_status_color (str, optional): Color code for the status label. Defaults to '#2b4463'.
            parent (QWidget, optional): Optional parent widget. Defaults to None.
        """
        super().__init__(parent)
        logger.debug("Initializing TaskContent widget.")

        if not task_status_color:
            task_status_color = default_task_status_color

        # Create a frame to hold the entire log content
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: #E1E1E8;
                border-radius: 5px;
            }
        """)

        # Frame layout
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(8, 5, 8, 5)
        frame_layout.setAlignment(Qt.AlignTop)

        # Header layout (Task Status + Username + Date)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 0, 5, 0)
        header_layout.setSpacing(20)

        status_label = QLabel(task_status)
        status_label.setStyleSheet(f"""
            background-color: {task_status_color}; 
            color: #E1E1E8; 
            font: bold 12px;
            padding: 2px 8px;
            border-radius: 5px;
        """)

        user_label = QLabel(username)
        user_label.setStyleSheet("color: black; font: bold 12px;")

        date_label = QLabel(date)
        date_label.setStyleSheet("color: gray; font: italic 11px;")

        header_layout.addWidget(status_label)
        header_layout.addWidget(user_label)
        header_layout.addStretch()
        header_layout.addWidget(date_label)

        # Comment
        comment_label = QLabel(comment)
        comment_label.setWordWrap(True)
        comment_label.setStyleSheet("color: black; font: 11px; padding-left: 5px;")

        # Add header & comment to the frame
        frame_layout.addLayout(header_layout)
        frame_layout.addWidget(comment_label)

        # Main layout for this widget
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 5, 0, 5)
        main_layout.addWidget(frame)


class TaskLogWidget(QWidget):
    """
    A widget that displays task logs in a QListWidget. Each log entry is
    represented by a TaskContent widget embedded as an item.
    """

    def __init__(self, parent: QWidget = None):
        """
        Initialize the TaskLogWidget.

        Args:
            parent (QWidget, optional): Optional parent widget. Defaults to None.
        """
        super().__init__(parent)
        logger.debug("Initializing TaskLogWidget.")

        self.setObjectName("TaskLogWidget")

        # Apply stylesheet to remove the border
        self.setStyleSheet("#TaskLogWidget { border: none; }")
        # Main layout
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)

        # QListWidget to hold the task log items
        self._list_widget = QListWidget()
        self._list_widget.setViewportMargins(0, 0, 10, 0)
        self._main_layout.addWidget(self._list_widget)

        # Internal data store for tasks
        self._tasks_data = []

    def get_tasks_data(self):
        """
        Get the current list of task logs data.

        Returns:
            list: The current task logs data as a list of dictionaries.
        """
        return self._tasks_data

    def set_tasks_data(self, tasks_data: list):
        """
        Set the list of task logs data and repopulate the list widget.

        Args:
            tasks_data (list): A list of dictionaries containing task data
                               (task_status, username, date, comment, etc.).
        """
        logger.debug(f"Setting tasks data: {tasks_data}")
        self._tasks_data = tasks_data
        self._populate_tasks()

    def _populate_tasks(self):
        """
        Clear and repopulate the list widget from self._tasks_data.
        """
        logger.debug("Populating the task list widget with task data.")
        self._list_widget.clear()

        for task in self._tasks_data:
            task_widget = TaskContent(
                task_status=task[TASK_STATUS],
                username=task[USERNAME],
                date=task[DATE],
                comment=task[COMMENT],
                task_status_color=task.get(STATUS_COLOR)
            )

            list_item = QListWidgetItem()
            list_item.setSizeHint(task_widget.sizeHint())
            self._list_widget.addItem(list_item)
            self._list_widget.setItemWidget(list_item, task_widget)


class MainWindow(QMainWindow):
    """
    Example MainWindow that demonstrates usage of TaskLogWidget
    to display multiple task log entries.
    """

    def __init__(self):
        """
        Initialize the main window and populate the TaskLogWidget
        with some sample task log data.
        """
        super().__init__()
        logger.debug("Initializing MainWindow.")

        self.setWindowTitle("Task Log with QListWidget")
        self.setGeometry(100, 100, 600, 400)

        # Main Task Log Widget
        self._task_log = TaskLogWidget()
        self.setCentralWidget(self._task_log)

        # Sample data to demonstrate usage
        sample_data = [
            {
                "status": "APPROVED",
                "username": "xyz",
                "date": "01-15 10:30",
                "comment": "Task approved for final submission.",
                "task_status_color": "green"
            },
            {
                "status": "REVIEW",
                "username": "pqr",
                "date": "01-10 09:45",
                "comment": "Reviewing progress for minor adjustments.",
                "task_status_color": "blue"
            },
            {
                "status": "DONE",
                "username": "lmn",
                "date": "01-18 11:00",
                "comment": "Final touchups completed.",
                "task_status_color": "green"
            },
            {
                "status": "APPROVED",
                "username": "xyz",
                "date": "01-15 10:30",
                "comment": "Task approved for final submission.",
                "task_status_color": "green"
            },
            {
                "status": "REVIEW",
                "username": "pqr",
                "date": "01-10 09:45",
                "comment": "Reviewing progress for minor adjustments.",
                "task_status_color": "orange"
            },
            {
                "status": "DONE",
                "username": "lmn",
                "date": "01-18 11:00",
                "comment": "Final touchups completed.",
                "task_status_color": "green"
            },
            {
                "status": "APPROVED",
                "username": "xyz",
                "date": "01-15 10:30",
                "comment": "Task approved for final submission.",
                "task_status_color": "green"
            },
            {
                "status": "REVIEW",
                "username": "pqr",
                "date": "01-10 09:45",
                "comment": "Reviewing progress for minor adjustments.",
                "task_status_color": "blue"
            },
            {
                "status": "DONE",
                "username": "lmn",
                "date": "01-18 11:00",
                "comment": "Final touchups completed.",
                "task_status_color": "green"
            }
        ]

        # Populate the TaskLogWidget with sample data
        self._task_log.set_tasks_data(sample_data)


if __name__ == "__main__":
    import sys

    # Configure logging for standalone testing (optional)
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
