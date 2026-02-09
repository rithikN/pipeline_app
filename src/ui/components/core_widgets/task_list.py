"""
task_list_widget.py

UI widget for displaying and interacting with tasks.
Delegates business logic (download/upload/asset tracker) to an injected controller.
"""

import logging
from typing import Dict, List
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QListWidgetItem,
    QMenu, QLineEdit
)
from PySide6.QtCore import Signal, Qt, QPoint
from PySide6.QtGui import QIcon, QAction, QPixmap

from ui.components.forms.task_list_form import Ui_TaskListForm
from ui.utils.stylesheet_utils import load_stylesheet
from ui.utils.task_filter import TaskFilter
from services.constants import TASK_NAME, TASK_STATUS, TASK_STATUS_NAME

logger = logging.getLogger(__name__)


class TaskListWidget(QWidget):
    """
    A widget that displays a list of tasks and their statuses.
    Users can search, filter, and select tasks.

    Emits only signals (UI-only). Business logic handled by controllers.
    """

    # Signals (UI → Controller)
    taskSelected = Signal(str, dict)      # (task_name, task_data)
    downloadRequested = Signal(dict)      # full task_data
    uploadRequested = Signal(dict)        # full task_data
    assetTrackerRequested = Signal(dict)  # full task_data

    def __init__(
        self,
        tasks: List[Dict] = None,
        task_status_colors: Dict[str, str] = None,
        parent: QWidget = None,
    ):
        """
        Initialize the TaskListWidget.

        Args:
            tasks (List[Dict], optional): A list of task dictionaries.
            task_status_colors (Dict[str, str], optional): Mapping from status to colors.
            parent (QWidget, optional): Optional parent widget.
        """
        super().__init__(parent)
        logger.debug("Initializing TaskListWidget.")

        # Internal state
        self._tasks = tasks or []
        self._task_status_colors = task_status_colors or {}

        # Setup UI
        self._ui = Ui_TaskListForm()
        self._ui.setupUi(self)

        # Expose UI elements
        self.task_listWidget = self._ui.task_listWidget
        self.search_lineEdit = self._ui.search_lineEdit

        # Private UI setup (icon, stylesheet, list config, context menu policy)
        self._setup_ui()

        # Setup signals
        self._setup_connections()
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
        # qss_path = Path.cwd() / "ui" / "stylesheets" / "task_list_widget.qss"
        # load_stylesheet(self, qss_path)
        load_stylesheet(self, r"ui\stylesheets\task_list_widget.qss")


        # Search icon
        pixmap = QPixmap("resources/icons/task_list/search.svg")
        if not pixmap.isNull():
            icon = QIcon(pixmap)
            action = QAction(icon, "", self.search_lineEdit)
            action.setIconVisibleInMenu(False)
            action.setIcon(icon)
            self.search_lineEdit.addAction(action, QLineEdit.LeadingPosition)

        # Task list config
        self.task_listWidget.setMinimumWidth(400)
        self.task_listWidget.setSpacing(5)
        self.task_listWidget.setViewportMargins(0, 0, 10, 0)
        self.task_listWidget.setContextMenuPolicy(Qt.CustomContextMenu)

    def _setup_connections(self):
        """
        Connect various signals to their respective slots.
        """
        logger.debug("Setting up signal connections for TaskListWidget.")
        self.task_listWidget.itemClicked.connect(self._emit_selected)
        self.task_listWidget.customContextMenuRequested.connect(self._show_context_menu)
        self.search_lineEdit.textChanged.connect(lambda text: self.filter_tasks(search_text=text))
        self.task_listWidget.currentItemChanged.connect(self._highlight_selected_item)

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
        logger.debug("Populating task list widget with tasks: %s", self._tasks)
        self.task_listWidget.clear()
        if not self._tasks:
            return

        for task in self._tasks:
            item_widget = self._create_task_widget(task[TASK_NAME], task[TASK_STATUS])
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
        task_widget.setStyleSheet("background-color: #E1E1E8; border-radius: 5px;")

        layout = QHBoxLayout(task_widget)
        layout.setContentsMargins(10, 5, 10, 5)

        # Task name
        name_label = QLabel(task_name)
        name_label.setStyleSheet("font-size: 14px; border: 0px;")
        layout.addWidget(name_label)

        # Spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)

        # Status
        print( task_status, TASK_STATUS_NAME)
        task_status[TASK_STATUS_NAME] = task_status[TASK_STATUS_NAME].upper()
        status_color = self._task_status_colors.get(task_status[TASK_STATUS_NAME], "gray")

        status_label = QLabel(task_status[TASK_STATUS_NAME])
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet(
            f"""
            background-color: {status_color};
            color: #E1E1E8;
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 5px;
            """
        )
        layout.addWidget(status_label)
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
    # Events, Slots & Context Menu
    # ------------------------------
    def _emit_selected(self, item: QListWidgetItem):
        """
        Emit taskSelected signal with the task name when an item is clicked.
        """

        # ToDo Please empty workfile list so that it always refresh correct workfiles,
        #  handle Could not determine task_code, here or in backend
        logger.debug(f"Task item clicked. {item}")
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
        if previous:
            prev_widget = self.task_listWidget.itemWidget(previous)
            if prev_widget:
                prev_widget.setStyleSheet("background-color: #E1E1E8; border-radius: 5px;")
        if current:
            curr_widget = self.task_listWidget.itemWidget(current)
            if curr_widget:
                curr_widget.setStyleSheet(
                    "border-radius: 5px; background-color: rgba(0, 120, 215, 0.1);"
                )

    def _show_context_menu(self, position: QPoint):
        """
        Display a context menu for the item at the given position.
        """

        logger.info("Showing context menu for a task item.")

        item = self.task_listWidget.itemAt(position)
        if not item:
            return
        task_data = item.data(Qt.UserRole)

        menu = QMenu(self)
        menu.addAction("Download Task Files", lambda: self.downloadRequested.emit(task_data))
        menu.addAction("Upload Input Files", lambda: self.uploadRequested.emit(task_data))
        menu.addSeparator()
        menu.addAction("Asset Tracker", lambda: self.assetTrackerRequested.emit(task_data))
        menu.exec(self.task_listWidget.mapToGlobal(position))


if __name__ == "__main__":
    import sys
    import logging
    from PySide6.QtWidgets import QApplication

    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)

    tasks = [
        {
            "name": "HL_BGL_Sc9998_Sh0040",
            "slug": "hl_bgl_sc9998_sh0040-24b3",
            "task_status": {"short_name": "TODO", "color": "#f5f5f5"},
        },
        {
            "name": "HL_Sc9998_Sh0070_COMP",
            "slug": "hl_sc9998_sh0070_comp-4abd",
            "task_status": {"short_name": "WIP", "color": "#E81123"},
        },
        {
            "name": "HL_Sc0940_Sh0020_TNL",
            "slug": "hl_sc0940_sh0020_tnl-4f64",
            "task_status": {"short_name": "HOLD", "color": "#442211"},
        },
    ]

    # Map status codes → colors (fallback)
    task_status_colors = {
        "TODO": "gray",
        "WIP": "red",
        "HOLD": "brown",
    }

    widget = TaskListWidget(tasks=tasks, task_status_colors=task_status_colors)

    widget.taskSelected.connect(lambda n, d: print("Selected:", n))
    widget.downloadRequested.connect(lambda d: print("Download:", d["name"]))
    widget.uploadRequested.connect(lambda d: print("Upload:", d["name"]))
    widget.assetTrackerRequested.connect(lambda d: print("Track assets for:", d["name"]))

    widget.show()
    sys.exit(app.exec())

