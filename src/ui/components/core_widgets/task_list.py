"""
task_list_widget.py

Provides the TaskListWidget class, which displays a searchable list of tasks
with color-coded statuses. Includes context menus for various actions.
"""

import logging
from typing import Dict, List
from PySide6.QtWidgets import (
    QWidget, QApplication, QHBoxLayout, QLabel, QSpacerItem,
    QSizePolicy, QListWidgetItem, QMenu, QLineEdit
)
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import  QIcon, QAction, QPixmap

from ui.components.forms.task_list_form import Ui_TaskListForm
from ui.utils.stylesheet_loader import load_stylesheet
from ui.utils.task_filter import TaskFilter
from services.constants import TASK_NAME, TASK_STATUS
logger = logging.getLogger(__name__)


class TaskListWidget(QWidget):
    """
    A widget that displays a list of tasks and their statuses.
    Users can search, filter, and select tasks.
    """

    taskSelected = Signal(str, dict)

    def __init__(
            self,
            tasks: List[Dict] = None,
            task_status_colors: Dict[str, str] = None,
            parent: QWidget = None
    ):
        """
        Initialize the TaskListWidget.

        Args:
            tasks (List[Dict], optional): A list of task dictionaries.
                Each dictionary should have 'task_name' and 'task_status' keys.
                Defaults to an empty list.
            task_status_colors (Dict[str, str], optional): A mapping from task status
                to a color string (e.g., "#FF0000"). Defaults to None.
            parent (QWidget, optional): Optional parent widget. Defaults to None.
        """
        super().__init__(parent)
        logger.debug("Initializing TaskListWidget.")

        # Create and set up the UI
        self._ui = Ui_TaskListForm()
        self._ui.setupUi(self)

        # Expose key UI elements for external usage
        self.task_listWidget = self._ui.task_listWidget
        self.search_lineEdit = self._ui.search_lineEdit

        # Internal state
        self._tasks = tasks if tasks else []
        self._task_status_colors = task_status_colors if task_status_colors else {}

        self._setup_ui()
        self._setup_connections()

        # Populate the tasks initially
        self._populate_tasks()

    # ------------------------------
    # Public Properties & Get/Set
    # ------------------------------

    def get_tasks(self) -> List[Dict]:
        """
        Returns the current list of tasks.
        """
        return self._tasks

    def set_tasks(self, tasks: List[Dict]):
        """
        Sets the task list and updates the UI.

        Args:
            tasks (List[Dict]): New list of tasks to display.
        """
        logger.debug(f"Setting tasks: {tasks}")
        self._tasks = tasks
        self._populate_tasks()

    def get_task_status_colors(self) -> Dict[str, str]:
        """
        Returns the current task status colors as a dict.
        """
        return self._task_status_colors

    def set_task_status_colors(self, task_status_colors: Dict[str, str]):
        """
        Sets the task status colors and refreshes the UI.

        Args:
            task_status_colors (Dict[str, str]): Mapping from status to color codes.
        """
        logger.debug(f"Setting task status colors: {task_status_colors}")
        self._task_status_colors = task_status_colors
        self._populate_tasks()  # Re-populate to reflect updated colors

    # ------------------------------
    # Private Setup & Connections
    # ------------------------------

    def _setup_ui(self):
        """
        Additional UI configuration after setting up from the .ui file.
        """
        logger.debug("Configuring UI elements and loading stylesheet.")
        self.setObjectName("TaskListWidget")

        # Load external stylesheet
        load_stylesheet(self, r"ui\stylesheets\task_list_widget.qss")

        pixmap = QPixmap("resources/icons/task_list/search.svg")
        if not pixmap.isNull():
            icon = QIcon(pixmap)
            action = QAction(icon, "", self.search_lineEdit)
            action.setIconVisibleInMenu(False)  # Hide in menus (optional)
            action.setIcon(icon)
            self.search_lineEdit.addAction(action, QLineEdit.LeadingPosition)

        # Configure the task_listWidget
        self.task_listWidget.setMinimumWidth(400)
        self.task_listWidget.setSpacing(5)
        self.task_listWidget.setViewportMargins(0, 0, 10, 0)
        self.task_listWidget.setContextMenuPolicy(Qt.CustomContextMenu)

    def _setup_connections(self):
        """
        Connect various signals to their respective slots.
        """
        logger.debug("Setting up signal connections for TaskListWidget.")
        self.task_listWidget.customContextMenuRequested.connect(self._show_context_menu)
        self.task_listWidget.itemClicked.connect(self._emit_task_selected)
        self.task_listWidget.currentItemChanged.connect(self._highlight_selected_item)
        self.search_lineEdit.textChanged.connect(self.filter_tasks)

    def set_icon(self):
        pixmap = QPixmap("resources/icons/task_list/search.svg")
        if not pixmap.isNull():
            icon = QIcon(pixmap)
            action = QAction(icon, "", self.search_lineEdit)
            action.setIconVisibleInMenu(False)  # Hide in menus (optional)
            action.setIcon(icon)
            self.search_lineEdit.addAction(action, QLineEdit.LeadingPosition)

    # ------------------------------
    # Private Helper Methods
    # ------------------------------

    def _populate_tasks(self):
        """
        Clears the list widget and repopulates it with the tasks.
        """
        logger.debug("Populating task list widget with tasks.")
        self.task_listWidget.clear()
        if not self._tasks:
            return

        for task in self._tasks:
            item_widget = self._create_task_widget(TASK_NAME, TASK_STATUS)
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            list_item.setData(Qt.UserRole, task)
            self.task_listWidget.addItem(list_item)
            self.task_listWidget.setItemWidget(list_item, item_widget)

    def _create_task_widget(self, task_name: str, task_status: str) -> QWidget:
        """
        Create a QWidget representing a single task item (name + status badge).

        Args:
            task_name (str): The name of the task.
            task_status (str): The status of the task.

        Returns:
            QWidget: A widget containing the name label and status badge.
        """
        logger.debug(f"Creating task widget for '{task_name}' with status '{task_status}'.")
        task_widget = QWidget()
        task_widget.setFixedHeight(34)
        task_widget.setStyleSheet(
            """
            background-color: #E1E1E8;
            border-radius: 5px;
            """
        )
        layout = QHBoxLayout(task_widget)
        layout.setContentsMargins(10, 5, 10, 5)

        # Task name label
        name_label = QLabel(task_name)
        name_label.setStyleSheet("font-size: 14px; border: 0px;")
        layout.addWidget(name_label)

        # Spacer to push the status label to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)

        # Task status label
        status_color = self._task_status_colors.get(task_status, "gray")
        task_status_label = QLabel(task_status)
        task_status_label.setAlignment(Qt.AlignCenter)
        task_status_label.setStyleSheet(
            f"""
            background-color: {status_color};
            color: #E1E1E8;
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 5px;
            """
        )
        layout.addWidget(task_status_label)

        return task_widget

    def _update_task_list_widget(self, tasks: List[Dict]):
        """
        Updates the list widget with a new subset of tasks, typically after filtering.
        """
        logger.debug("Updating the task list widget with filtered tasks.")
        self.task_listWidget.clear()
        for task in tasks:
            item_widget = self._create_task_widget(task[TASK_NAME], task[TASK_STATUS])
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            list_item.setData(Qt.UserRole, task)
            self.task_listWidget.addItem(list_item)
            self.task_listWidget.setItemWidget(list_item, item_widget)

    # ------------------------------
    # Public Methods
    # ------------------------------

    def filter_tasks(self, search_text: str = "", selection: dict = None):
        """
        Filters the task list based on search text and active selection filters.

        Args:
            search_text (str, optional): The text to search for within tasks. Defaults to "".
            selection (dict, optional): Additional filter criteria. Defaults to None.
        """
        logger.debug(f"Filtering tasks with search_text='{search_text}' and selection={selection}")
        task_filter = TaskFilter(self._tasks)
        filtered_tasks = task_filter.filter(search_text, selection)
        self._update_task_list_widget(filtered_tasks)

    def set_selected_task(self, task_name: str, emit_signal: bool = False):
        """
        Programmatically select a task in the list.

        Args:
            task_name (str): The name of the task to select.
            emit_signal (bool, optional): Whether to emit the taskSelected signal
                after selection. Defaults to False.
        """
        logger.debug(f"Setting selected task to '{task_name}', emit_signal={emit_signal}.")
        found_item = None
        task_data = None
        for i in range(self.task_listWidget.count()):
            item = self.task_listWidget.item(i)
            task_data = item.data(Qt.UserRole)
            if task_data and task_data.get(TASK_NAME) == task_name:
                found_item = item
                break

        if found_item:
            self.task_listWidget.setCurrentItem(found_item)
            if emit_signal:
                self.taskSelected.emit(task_name, task_data)
        else:
            self.task_listWidget.clearSelection()
            logger.info(f"Task '{task_name}' not found in the list.")

    # ------------------------------
    # Event Handlers & Slots
    # ------------------------------

    def _emit_task_selected(self, item: QListWidgetItem):
        """
        Emit taskSelected signal with the task name when an item is clicked.
        """
        logger.debug("Task item clicked.")
        if not item:
            return

        task_data = item.data(Qt.UserRole)
        item_widget = self.task_listWidget.itemWidget(item)
        if item_widget:
            name_label = item_widget.findChild(QLabel)

            if name_label:
                task_name = name_label.text()
                self.taskSelected.emit(task_name, task_data)

    def _highlight_selected_item(self, current: QListWidgetItem, previous: QListWidgetItem):
        """
        Update style to highlight the newly selected item and unhighlight the previous one.
        """
        logger.debug("Highlighting selected item and unhighlighting previous one.")
        # Unhighlight previous
        if previous:
            prev_widget = self.task_listWidget.itemWidget(previous)
            if prev_widget:
                prev_widget.setStyleSheet(
                    """
                    background-color: #E1E1E8;
                    border-radius: 5px;
                    """
                )

        # Highlight current
        if current:
            curr_widget = self.task_listWidget.itemWidget(current)
            if curr_widget:
                curr_widget.setStyleSheet(
                    """
                    border-radius: 5px;
                    background-color: rgba(0, 120, 215, 0.1); /* Light highlight */
                    """
                )

    def _show_context_menu(self, position: QPoint):
        """
        Display a context menu for the item at the given position.
        """
        logger.debug("Showing context menu for a task item.")
        item = self.task_listWidget.itemAt(position)
        if item:
            # Create the context menu
            context_menu = QMenu(self)

            # Add actions
            open_action = QAction("Open Task", self)
            delete_action = QAction("Delete Task", self)
            mark_done_action = QAction("Mark as Done", self)

            # Connect actions
            open_action.triggered.connect(lambda: self.open_task(item))
            delete_action.triggered.connect(lambda: self.delete_task(item))
            mark_done_action.triggered.connect(lambda: self.mark_task_done(item))

            # Add to the context menu
            context_menu.addAction(open_action)
            context_menu.addAction(delete_action)
            context_menu.addAction(mark_done_action)

            context_menu.exec(self.task_listWidget.mapToGlobal(position))

    # ------------------------------
    # Context Menu Action Handlers
    # ------------------------------

    def open_task(self, item: QListWidgetItem):
        """
        Handles the 'Open Task' action from the context menu.
        """
        logger.debug(f"Open Task action triggered for item data: {item.data(Qt.UserRole)}")
        print(f"Opening task: {item.data(Qt.UserRole)}")

    def delete_task(self, item: QListWidgetItem):
        """
        Handles the 'Delete Task' action from the context menu.
        """
        logger.debug(f"Delete Task action triggered for item text: {item.text()}")
        print(f"Deleting task: {item.text()}")

    def mark_task_done(self, item: QListWidgetItem):
        """
        Handles the 'Mark as Done' action from the context menu.
        """
        logger.debug(f"Mark Task Done action triggered for item text: {item.text()}")
        print(f"Marking task as done: {item.text()}")


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)

    # Example tasks
    tasks = [
        {"task_name": "prj_e000_sc000_sh0000_task", "task_status": "NYS"},
        {"task_name": "prj_e014_sc001_sh0010_lay", "task_status": "APP"},
        {"task_name": "prj_e410_SC010_sh0145_bgl", "task_status": "EXT_RTK"},
        {"task_name": "prj_sq0910_sh0562_abc", "task_status": "WFA"},
        {"task_name": "prj_SEQ0450_SH1480_cmp", "task_status": "IN FARM"},
    ]
    task_status_colors = {
        "NYS": "blue",
        "APP": "green",
        "EXT_RTK": "red",
        "WFA": "orange",
        "IN FARM": "brown"
    }

    window = TaskListWidget(tasks, task_status_colors)
    window.show()
    sys.exit(app.exec())
