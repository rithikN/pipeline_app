"""
work_files_widget.py

Defines a WorkFilesWidget that displays a list of file items
(each with an application icon, version, etc.) and handles sorting
and selection signals.
"""

import logging
from typing import List, Dict, Optional

from PySide6.QtWidgets import (
    QWidget, QApplication, QHBoxLayout, QLabel, QSpacerItem,
    QSizePolicy, QListWidgetItem, QPushButton
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon

from ui.components.forms.work_files_form import Ui_WorkFilesForm
from ui.utils.stylesheet_loader import load_stylesheet
from services.constants import WORK_APP, WORK_VERSION, WORK_SIZE, WORK_DATE, SOFTWARE_ICON_DATA
from services.data_service import create_file
from ui.components.extensions.message_box import MessageBox

# Optional: Configure a module-level logger
logger = logging.getLogger(__name__)


class WorkFilesWidget(QWidget):
    """
    Displays a list of work files, each with an application icon,
    version, size, and date. Supports sorting and emits signals
    upon selection.
    """

    fileSelected = Signal(dict)
    fileDeselected = Signal()

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        files: Optional[List[Dict]] = None,
        task_data: dict = {}  # Add task_selected as an argument with a default value
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

        self.message_box = MessageBox()

        # Instantiate and set up the auto-generated form
        self._ui = Ui_WorkFilesForm()
        self._ui.setupUi(self)
        self.task_data = task_data

        # Expose the key UI elements for external usage
        self.workFiles_listWidget = self._ui.workFiles_listWidget
        self.sort_comboBox = self._ui.sort_comboBox

        # Default app icons
        self._app_data = SOFTWARE_ICON_DATA

        # Store the list of files
        self._files = files if files else []

        self._setup_ui()
        self._setup_connections()

        # Populate the files initially
        self.populate_files()

    def _setup_ui(self):
        """
        Configure the UI elements, including stylesheet and widget properties.
        """
        logger.debug("Setting up UI for WorkFilesWidget.")
        load_stylesheet(self, r"ui\stylesheets\work_files_widget.qss")
        self.setFixedWidth(200)
        self.workFiles_listWidget.setSpacing(5)
        self.workFiles_listWidget.setViewportMargins(0, 0, 10, 0)

        self.sort_comboBox.addItems(["By Version", "By Size", "By Date"])

        # Trigger re-population when combo box changes
        self.sort_comboBox.currentIndexChanged.connect(self.populate_files)

    def _setup_connections(self):
        """
        Connect signals from the UI to corresponding slots.
        """
        logger.debug("Setting up signal connections for WorkFilesWidget.")
        # On list item click, emit both an item text signal and a fileSelected signal
        self.workFiles_listWidget.itemClicked.connect(lambda item: self.fileSelected.emit(item.text()))
        self.workFiles_listWidget.itemClicked.connect(self._emit_workfiles_selected)
        self.workFiles_listWidget.currentItemChanged.connect(self._highlight_selected_item)

    # -----------------------------
    # Public Properties
    # -----------------------------

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

    # -----------------------------
    # Public Methods
    # -----------------------------

    def populate_files(self):
        """
        Populate the list widget with the stored files, applying any sorting first.
        Resets selection as well.
        """
        logger.debug("Populating files in WorkFilesWidget.")

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
                item_widget = self._create_file_widget(
                    file_data[WORK_APP],
                    file_data[WORK_VERSION],
                    file_data[WORK_SIZE],
                    file_data[WORK_DATE],
                )
                list_item = QListWidgetItem()
                list_item.setSizeHint(item_widget.sizeHint())
                list_item.setData(Qt.UserRole, file_data)  # Store metadata
                self.workFiles_listWidget.addItem(list_item)
                self.workFiles_listWidget.setItemWidget(list_item, item_widget)

            # Deselect all items visually
            self._deselect_items()

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
        create_button.clicked.connect(self._handle_create_file)
        create_button.setStyleSheet("""
            #createFileButton {
                font-size: 14px;
                background-color: #226583;
                border-radius: 5px;
                border: none;
                color: white;
            }
            #createFileButton:hover,
            #createFileButton:pressed,
            #createFileButton:checked,
            3createFileButton:focus {
                background-color: #226583;
                outline: none;
            }
        """)
        list_item = QListWidgetItem()
        list_item.setSizeHint(create_button.sizeHint())
        self.workFiles_listWidget.addItem(list_item)
        self.workFiles_listWidget.setItemWidget(list_item, create_button)

    def set_task_data(self, task_data: dict):
        """
        Set the task_selected property.

        Args:
            task_data (dict): Selected task Data.
        """
        logger.debug(f"Setting task_selected to {task_data}.")
        self.task_data = task_data

    def _handle_create_file(self):
        """
        Handle the 'Create File' button click. This function will
        call the backend API to create a new file.
        """
        logger.debug("Create File button clicked.")
        response = create_file(self.task_data)

        self.message_box.show_message(
            "Yet To Implement",
            message_type="info",
            title="Create File"
        )

    # -----------------------------
    # Internal Helper Methods
    # -----------------------------

    def _create_file_widget(self, app: str, version: str, size: str, date: str) -> QWidget:
        """
        Create a custom widget representing a single file entry, with an app icon and version label.

        Args:
            app (str): The application name (e.g., "Blender", "Maya").
            version (str): The version string (e.g., "v013").
            size (str): The file size (e.g., "700").
            date (str): The date string.

        Returns:
            QWidget: A QWidget containing the file's representation.
        """
        logger.debug(f"Creating file widget for app={app}, version={version}, size={size}, date={date}.")
        file_widget = QWidget()
        file_widget.setFixedHeight(34)
        file_widget.setStyleSheet("""
            background-color: #E1E1E8;
            border-radius: 5px;
        """)
        layout = QHBoxLayout(file_widget)
        layout.setContentsMargins(10, 5, 10, 5)

        # Application icon
        icon_label = QLabel()
        icon_label.setStyleSheet("border: 0px;")
        icon_path = self._app_data.get(app, None)
        if icon_path:
            icon_label.setPixmap(QIcon(icon_path).pixmap(22, 22))
        layout.addWidget(icon_label)

        # Version label
        version_label = QLabel(str(version))
        version_label.setStyleSheet("font-size: 14px; border: 0px; padding-left: 10px;")
        layout.addWidget(version_label)

        # Spacer to push other info to the right (if needed)
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)

        return file_widget

    def _sort_files(self):
        """
        Sort the files based on the selected criteria in the sort_comboBox.
        """
        criteria = self.sort_comboBox.currentText()
        logger.debug(f"Sorting files by criteria: {criteria}")
        if criteria == "By Version":
            self._files.sort(key=lambda x: x["version"])
        elif criteria == "By Size":
            self._files.sort(key=lambda x: x["size"])
        elif criteria == "By Date":
            self._files.sort(key=lambda x: x["date"])

    def _emit_workfiles_selected(self, item: QListWidgetItem):
        """
        Emit the fileSelected signal with the file data (UserRole)
        of the currently selected item.
        """
        logger.debug("Emitting fileSelected signal for the clicked item.")
        if not item:
            self.fileSelected.emit({})
            return

        file_data = item.data(Qt.UserRole)
        if file_data:
            self.fileSelected.emit(file_data)
        else:
            self.fileSelected.emit({})

    def _highlight_selected_item(self, current: QListWidgetItem, previous: QListWidgetItem):
        """
        Highlight the newly selected item, and reset the previous one.
        """
        logger.debug("Highlighting newly selected item and unhighlighting the previous one.")

        # Reset previous
        if previous:
            prev_widget = self.workFiles_listWidget.itemWidget(previous)
            if prev_widget:
                prev_widget.setStyleSheet(
                    """
                    background-color: #E1E1E8;
                    border-radius: 5px;
                    """
                )

        # Highlight current
        if current:
            curr_widget = self.workFiles_listWidget.itemWidget(current)
            if curr_widget:
                curr_widget.setStyleSheet(
                    """
                    border-radius: 5px;
                    background-color: rgba(0, 120, 215, 0.1); /* Light highlight */
                    """
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
                    """
                    background-color: #E1E1E8;
                    border: 1px solid #252B36;
                    border-radius: 5px;
                    """
                )


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)

    files_data = [
        {"app": "Blender", "version": "v182", "size": 1500, "date": "2024-12-10"},
        {"app": "Blender", "version": "v054", "size": 800,  "date": "2024-11-30"},
        {"app": "After Effects", "version": "v032", "size": 1200, "date": "2024-10-25"},
        {"app": "After Effects", "version": "v029", "size": 1100, "date": "2024-09-12"},
        {"app": "DaVinci", "version": "v027", "size": 950,  "date": "2024-08-01"},
        {"app": "Maya", "version": "v013",   "size": 700,  "date": "2024-07-15"},
        {"app": "Maya", "version": "v012",   "size": 680,  "date": "2024-06-22"},
        {"app": "Nuke", "version": "v009",   "size": 500,  "date": "2024-05-18"},
        {"app": "Photoshop", "version": "v008", "size": 450, "date": "2024-04-10"},
        {"app": "DaVinci", "version": "v006",  "size": 300, "date": "2024-03-05"},
    ]
    files_data = []

    widget = WorkFilesWidget(files=files_data, task_data={"t": "True"})
    widget.show()
    sys.exit(app.exec())
