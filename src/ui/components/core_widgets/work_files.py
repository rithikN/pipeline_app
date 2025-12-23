"""
work_files_widget.py

Defines a WorkFilesWidget that displays a list of file items
(each with an application icon, version, etc.) and handles sorting
and selection signals.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QWidget, QApplication, QHBoxLayout, QLabel, QSpacerItem,
    QSizePolicy, QListWidgetItem, QPushButton, QMenu
)
from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtGui import QIcon, QCursor

from ui.components.forms.work_files_form import Ui_WorkFilesForm
from ui.utils.stylesheet_utils import load_stylesheet
from services.constants import (
    WORK_APP, WORK_VERSION, WORK_SIZE, WORK_DATE,
    WORK_FILE_DETAIL, WORK_FILE_NAME, SOFTWARE_ICON_DATA
)

logger = logging.getLogger(__name__)


class WorkFilesWidget(QWidget):
    """
    Displays a list of work files, each with an application icon,
    version, size, and date. Supports sorting and emits signals
    upon selection.
    """

    # Signals for controller wiring
    createRequested = Signal(dict)     # emits task_data
    downloadRequested = Signal(dict)   # emits file_data
    uploadRequested = Signal(dict)     # emits file_data
    fileSelected = Signal(dict)        # emits file_data
    refreshRequested = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        files: Optional[List[Dict]] = None,
        task_data: dict = None,
    ):
        """
        Initialize the WorkFilesWidget.

        Args:
            parent (QWidget, optional): The parent widget, if any.
            files (List[Dict], optional): A list of file data dictionaries. Defaults to empty.
            task_data (Dict, optional): task_data.
        """
        super().__init__(parent)
        logger.debug("Initializing WorkFilesWidget.")
        self._ui = Ui_WorkFilesForm()
        self._ui.setupUi(self)

        self.task_data = task_data or {}
        self._files = files or []
        self._app_data = SOFTWARE_ICON_DATA

        # Expose key UI elements
        self.workFiles_listWidget = self._ui.workFiles_listWidget
        self.sort_comboBox = self._ui.sort_comboBox

        self._setup_ui()
        self._setup_connections()
        self.populate_files()

    # ---------------------------
    # Setup
    # ---------------------------
    def _setup_ui(self):
        """
        Configure the UI elements, including stylesheet and widget properties.
        """
        logger.debug("Setting up UI for WorkFilesWidget.")
        qss_path = Path.cwd() / "ui" / "stylesheets" / "work_files_widget.qss" # ToDo Fix qss path
        load_stylesheet(self, qss_path)

        self.setFixedWidth(200)
        self.workFiles_listWidget.setSpacing(5)
        self.workFiles_listWidget.setViewportMargins(0, 0, 10, 0)
        self.workFiles_listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sort_comboBox.addItems(["By Version", "By Size", "By Date"])
        self.sort_comboBox.currentIndexChanged.connect(self.populate_files)

    def _setup_connections(self):
        """
        Connect signals from the UI to corresponding slots.
        """
        logger.debug("Setting up signal connections for WorkFilesWidget.")
        self.workFiles_listWidget.customContextMenuRequested.connect(self._show_context_menu)
        self.workFiles_listWidget.itemClicked.connect(self._emit_selected)
        self.workFiles_listWidget.currentItemChanged.connect(self._highlight_selected_item)

    # ---------------------------
    # Public API
    # ---------------------------
    @property
    def files(self) -> List[Dict]:
        """
        The current list of files displayed by this widget.

        Returns:
            List[Dict]: A list of file data dictionaries.
        """
        return self._files

    @files.setter
    def files(self, value: List[Dict]):
        """
        Set the list of files and repopulate the widget.

        Args:
            value (List[Dict]): A list of file data dictionaries.

        Raises:
            ValueError: If value is not a list.
        """
        if not isinstance(value, list):
            raise ValueError("Files must be a list")
        logger.debug(f"Setting files: {value}")

        self._files = value
        self.populate_files()

    # ---------------------------
    # Public Methods
    # ---------------------------
    def set_task_data(self, task_data: dict):
        self.task_data = task_data or {}

    def populate_files(self):
        """
        Populate the list widget with the stored files, applying any sorting first.
        Resets selection as well.
        """
        logger.debug(f"Populating files in WorkFilesWidget with task_data: {self.task_data} and files: {self.files}")

        # Clear current selection and emit deselect
        if self.workFiles_listWidget.currentItem():
            self.workFiles_listWidget.setCurrentItem(None)
            self.fileSelected.emit({})

        self.workFiles_listWidget.clear()

        # Check if files are empty and task is selected
        if not self._files and self.task_data:
            self._add_create_file_button()
        elif self._files:
            # Sort files based on the current combo box choice
            self._sort_files()

            # Create list items for each file
            for file_data in self._files:
                ext = Path(file_data[WORK_FILE_DETAIL][WORK_FILE_NAME]).suffix
                item_widget = self._create_file_widget(
                    file_data[WORK_APP], ext,
                    file_data[WORK_VERSION],
                    file_data[WORK_SIZE],
                    file_data[WORK_DATE],
                )
                list_item = QListWidgetItem()
                list_item.setSizeHint(item_widget.sizeHint())
                list_item.setData(Qt.UserRole, file_data)  # Store metadata
                self.workFiles_listWidget.addItem(list_item)
                self.workFiles_listWidget.setItemWidget(list_item, item_widget)
            self._deselect_items()

    # ---------------------------
    # Private Helpers
    # ---------------------------

    def _add_create_file_button(self):
        """
        Add a 'Create File' button to the list widget if it doesn't already exist.
        """
        logger.debug("Adding 'Create File' button.")

        # Check if 'Create File' button already exists
        for index in range(self.workFiles_listWidget.count()):
            item = self.workFiles_listWidget.item(index)
            widget = self.workFiles_listWidget.itemWidget(item)
            if isinstance(widget, QPushButton) and widget.text() == "Create File":
                logger.debug("'Create File' button already exists. Skipping addition.")
                return

        # Add the button if it doesn't exist
        create_button = QPushButton("Create File")
        create_button.setObjectName("createFileButton")
        create_button.setIcon(QIcon("resources/icons/work_list/create_file.svg"))
        create_button.setIconSize(QSize(20, 20))
        create_button.setCursor(QCursor(Qt.PointingHandCursor))
        create_button.clicked.connect(lambda: self.createRequested.emit(self.task_data))

        list_item = QListWidgetItem()
        list_item.setSizeHint(create_button.sizeHint())
        self.workFiles_listWidget.addItem(list_item)
        self.workFiles_listWidget.setItemWidget(list_item, create_button)

    def _create_file_widget(self, app: str, ext: str, version: str, size: str, date: str) -> QWidget:
        """
        Create a custom widget representing a single file entry, with an app icon and version label.

        Args:
            app (str): The application name (e.g., "Blender", "Maya").
            ext (str): The application extension (e.g., ".blend", ".ma").
            version (str): The version string (e.g., "v013").
            size (str): The file size (e.g., "700").
            date (str): The date string.

        Returns:
            QWidget: A QWidget containing the file's representation.
        """
        logger.debug(f"Creating file widget for app={app}, ext={ext}, version={version}, size={size}, date={date}.")
        file_widget = QWidget()
        file_widget.setFixedHeight(34)
        file_widget.setStyleSheet("background-color: #E1E1E8; border-radius: 5px;")

        layout = QHBoxLayout(file_widget)
        layout.setContentsMargins(10, 5, 10, 5)

        # Application icon
        icon_label = QLabel()
        icon_label.setStyleSheet("border: 0px;")
        icon_path = self._app_data.get(ext, "resources/icons/menu_bar/missing.svg")
        icon_label.setPixmap(QIcon(icon_path).pixmap(22, 22))
        layout.addWidget(icon_label)

        # Version
        version_label = QLabel(str(version))
        version_label.setStyleSheet("font-size: 14px; border: 0px; padding-left: 10px;")
        layout.addWidget(version_label)

        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        return file_widget

    def _sort_files(self):
        """
        Sort the files based on the selected criteria in the sort_comboBox.
        """
        criteria = self.sort_comboBox.currentText()
        logger.debug(f"Sorting files by: {criteria}")
        if criteria == "By Version":
            self._files.sort(key=lambda x: x["version"])
        elif criteria == "By Size":
            self._files.sort(key=lambda x: x["size"])
        elif criteria == "By Date":
            self._files.sort(key=lambda x: x["date"])

    # ---------------------------
    # Event Handlers
    # ---------------------------
    def _show_context_menu(self, pos: QPoint):
        item = self.workFiles_listWidget.itemAt(pos)
        if not item:
            return
        file_data = item.data(Qt.UserRole)

        menu = QMenu(self)
        if not file_data.get("slug"):
            menu.addAction("Create File", lambda: self.createRequested.emit(self.task_data))
        else:
            menu.addAction("Download File", lambda: self.downloadRequested.emit(file_data))
            menu.addAction("Upload File", lambda: self.uploadRequested.emit(file_data))
        menu.exec(self.workFiles_listWidget.mapToGlobal(pos))

    def _emit_selected(self, item: QListWidgetItem):
        if not item:
            self.fileSelected.emit({})
            return

        file_data = item.data(Qt.UserRole)
        if file_data:
            self.fileSelected.emit(file_data)

    def _highlight_selected_item(self, current: QListWidgetItem, previous: QListWidgetItem):
        """
        Highlight the newly selected item, and reset the previous one.
        """
        logger.debug("Highlighting newly selected item and unhighlighting the previous one.")

        # Reset previous
        if previous:
            prev_widget = self.workFiles_listWidget.itemWidget(previous)
            if prev_widget:
                prev_widget.setStyleSheet("background-color: #E1E1E8; border-radius: 5px;")

        # Highlight current
        if current:
            curr_widget = self.workFiles_listWidget.itemWidget(current)
            if curr_widget:
                curr_widget.setStyleSheet(
                    "border-radius: 5px; background-color: rgba(0, 120, 215, 0.1);"
                )

    def _deselect_items(self):
        """
        Deselect and reset the style of all items in the list.
        """
        logger.debug("Deselecting all items in WorkFilesWidget.")
        for index in range(self.workFiles_listWidget.count()):
            item = self.workFiles_listWidget.item(index)
            widget = self.workFiles_listWidget.itemWidget(item)
            if widget:
                widget.setStyleSheet(
                    "background-color: #E1E1E8; border: 1px solid #252B36; border-radius: 5px;"
                )

    # --------------------
    # Event Handlers & Slots
    # --------------------

    def _show_context_menu(self, pos: QPoint):
        """
        Show a context menu when the user right-clicks on a list item or empty space.

        Args:
            position (QPoint): The mouse click position.
        """
        item = self.workFiles_listWidget.itemAt(pos)
        if not item:
            return

        file_data = item.data(Qt.UserRole) or {}
        menu = QMenu(self)

        if not file_data.get("slug"):
            menu.addAction("Create File", lambda: self.createRequested.emit(self.task_data))
        else:
            menu.addAction("Download File", lambda: self.downloadRequested.emit(file_data))
            menu.addAction("Upload File", lambda: self.uploadRequested.emit(file_data))

        menu.addSeparator()
        menu.addAction("Refresh List", self._on_refresh_action)

        menu.exec(self.workFiles_listWidget.mapToGlobal(pos))

    def _on_refresh_action(self):
        """
        Handles the 'Refresh work file list' action from the context menu.
        """
        # self.files = []  # please make sure you pass new create file along with existing file
        self.message_box.show_message(
            "Yet To Implement",
            message_type="info",
            title="Open"
        )
        pass


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)

    files_data = [
        {"app_name": "Blender", "version": "v182", "file_size": 1500, "date": "2024-12-10", 'slug':'test', "work_detail": {"file_name": "file1.blend"}},
        {"app_name": "Maya", "version": "v013", "file_size": 700, "date": "2024-07-15", "work_detail": {"file_name": "file2.ma"}},
    ]
    # files_data = []

    widget = WorkFilesWidget(files=files_data, task_data={"name": "TestTask"})
    widget.createRequested.connect(lambda td: print("Create requested for", td))
    widget.downloadRequested.connect(lambda fd: print("Download requested for", fd))
    widget.uploadRequested.connect(lambda fd: print("Upload requested for", fd))
    widget.fileSelected.connect(lambda fd: print("File selected:", fd))

    widget.show()
    sys.exit(app.exec())
