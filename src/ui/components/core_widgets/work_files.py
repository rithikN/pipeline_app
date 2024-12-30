# src/ui/components/work_file_widget.py
from PySide6.QtWidgets import QWidget, QApplication, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, \
    QListWidgetItem
from PySide6.QtCore import Signal, Qt
from ui.components.forms.work_files_form import Ui_WorkFilesForm
from PySide6.QtGui import QIcon

from ui.utils.stylesheet_loader import load_stylesheet
from services.constants import WORK_APP, WORK_VERSION, WORK_SIZE, WORK_DATE


class WorkFilesWidget(QWidget, Ui_WorkFilesForm):
    fileSelected = Signal(dict)
    fileDeselected = Signal()

    def __init__(self, files=None):
        super().__init__()

        self.app_data = {
            "Blender": "resources/icons/blender.png",
            "After Effects": "resources/icons/after-effects.png",
            "DaVinci": "resources/icons/davinci-resolve.png",
            "Maya": r"C:\Users\sknay\PycharmProjects\pipeline_app\src\resources\icons\maya.png",
            "Nuke": "resources/icons/nuke.png",
            "Photoshop": "resources/icons/photoshop.png",
        }

        # Initialize file data
        self._files = files if files else []

        self.init_ui()
        self.connections()
        self.populate_files()

    def init_ui(self):
        """Initialize the UI elements of the task list widget."""
        self.setupUi(self)
        load_stylesheet(self, r"ui\stylesheets\work_files_widget.qss")
        self.setFixedWidth(200)
        self.workFiles_listWidget.setSpacing(5)
        self.sort_comboBox.addItems(["By Version", "By Size", "By Date"])
        self.sort_comboBox.currentIndexChanged.connect(self.populate_files)

    def connections(self):
        self.workFiles_listWidget.itemClicked.connect(lambda item: self.fileSelected.emit(item.text()))
        self.workFiles_listWidget.itemClicked.connect(self.emit_workfiles_selected)
        self.workFiles_listWidget.currentItemChanged.connect(self.highlight_selected_item)

    @property
    def files(self):
        return self._files

    @files.setter
    def files(self, value):
        if isinstance(value, list):
            self._files = value
            self.populate_files()
        else:
            raise ValueError("Files must be a list")

    def populate_files(self):
        """Populate the file list widget."""

        if self.workFiles_listWidget.currentItem():
            self.workFiles_listWidget.setCurrentItem(None)
            self.fileSelected.emit({})

        self.workFiles_listWidget.clear()

        self.sort_files()

        for file in self.files:
            item_widget = self.create_file_widget(
                file[WORK_APP], file[WORK_VERSION], file[WORK_SIZE], file[WORK_DATE]
            )
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            print(list_item.sizeHint())
            list_item.setData(Qt.UserRole, file)  # Store metadata
            self.workFiles_listWidget.addItem(list_item)
            self.workFiles_listWidget.setItemWidget(list_item, item_widget)

        self.deselect_item()

    def create_file_widget(self, app, version, size, date):
        """Create a custom widget for a file."""
        file_widget = QWidget()
        file_widget.setFixedHeight(34)
        file_widget.setStyleSheet("""
            background-color: #E1E1E8;
            border-radius: 5px;
            """)
        layout = QHBoxLayout(file_widget)
        layout.setContentsMargins(10, 5, 10, 5)

        # Icon
        icon_label = QLabel()
        icon_label.setStyleSheet("border: 0px;")
        icon_label.setPixmap(QIcon(self.app_data[app]).pixmap(22, 22))  # App icon
        layout.addWidget(icon_label)

        # Version label
        version_label = QLabel(str(version))
        version_label.setStyleSheet("font-size: 14px; border: 0px; padding-left: 10px;")
        layout.addWidget(version_label)

        # Spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)

        return file_widget

    def sort_files(self):
        """Sort the files based on the selected criteria."""
        criteria = self.sort_comboBox.currentText()
        if criteria == "By Version":
            self.files.sort(key=lambda x: x["version"])
        elif criteria == "By Size":
            self.files.sort(key=lambda x: x["size"])
        elif criteria == "By Date":
            self.files.sort(key=lambda x: x["date"])

    def emit_workfiles_selected(self, item):
        """Emit taskSelected signal with the task name."""
        if item:
            file_data = item.data(Qt.UserRole)
            print(file_data, '1111111112')
            workFile_widget = self.workFiles_listWidget.itemWidget(item)
            if workFile_widget and file_data:
                self.fileSelected.emit(file_data)
            else:
                self.fileSelected.emit({})

    def highlight_selected_item(self, current, previous):
        """Highlight the selected item."""
        if previous:
            # Reset previous item's background
            previous_widget = self.workFiles_listWidget.itemWidget(previous)
            if previous_widget:
                previous_widget.setStyleSheet(
                    """
                    background-color: #E1E1E8;
                    border: 1px solid #252B36;
                    border-radius: 5px;
                    """
                )

        if current:
            # Highlight current item's background
            current_widget = self.workFiles_listWidget.itemWidget(current)
            if current_widget:
                current_widget.setStyleSheet(
                    """
                    border: 2px solid #0078D7;  /* Highlight border */
                    border-radius: 5px;
                    background-color: rgba(0, 120, 215, 0.1);  /* Light highlight */
                    """
                )

    def deselect_item(self):
        """Deselect and reset the styles of all items."""
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
    app = QApplication([])

    files_data = [
        {"app": "Blender", "version": "v182", "size": 1500, "date": "2024-12-10"},
        {"app": "Blender", "version": "v054", "size": 800, "date": "2024-11-30"},
        {"app": "After Effects", "version": "v032", "size": 1200, "date": "2024-10-25"},
        {"app": "After Effects", "version": "v029", "size": 1100, "date": "2024-09-12"},
        {"app": "DaVinci", "version": "v027", "size": 950, "date": "2024-08-01"},
        {"app": "Maya", "version": "v013", "size": 700, "date": "2024-07-15"},
        {"app": "Maya", "version": "v012", "size": 680, "date": "2024-06-22"},
        {"app": "Nuke", "version": "v009", "size": 500, "date": "2024-05-18"},
        {"app": "Photoshop", "version": "v008", "size": 450, "date": "2024-04-10"},
        {"app": "DaVinci", "version": "v006", "size": 300, "date": "2024-03-05"},
    ]

    widget = WorkFilesWidget(files=files_data)
    widget.show()
    app.exec()
