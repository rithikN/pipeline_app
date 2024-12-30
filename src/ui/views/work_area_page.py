from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QScrollArea, QApplication, QTabWidget, QLabel, QFrame
)
from PySide6.QtCore import Qt

from ui.components.extensions.custom_line import GradientLineWidget


class WorkAreaWidget(QWidget):
    def __init__(self, selection_widget, task_list_widget, work_file_widget, work_file_detail_widget,
                 file_preview_widget):
        """
        Initialize WorkAreaWidget with pre-initialized components.
        """
        super().__init__()
        self.selection_widget = selection_widget
        self.task_list_widget = task_list_widget
        self.work_file_widget = work_file_widget
        self.work_file_detail_widget = work_file_detail_widget
        self.file_preview_widget = file_preview_widget

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        top_line = GradientLineWidget()

        # Wrap Selection Widget
        selection_wrapper = QWidget()
        selection_layout = QVBoxLayout()
        selection_layout.setContentsMargins(0, 0, 0, 0)
        selection_layout.addWidget(self.selection_widget)
        selection_wrapper.setLayout(selection_layout)
        selection_wrapper.setFixedHeight(50)

        # Shared container for work_file_detail_widget and file_preview_widget
        shared_container = QWidget()
        shared_container.setObjectName(u"shared_container")
        shared_layout = QVBoxLayout()
        shared_layout.setContentsMargins(0, 0, 0, 0)
        shared_layout.addWidget(self.work_file_detail_widget)
        shared_layout.addWidget(self.file_preview_widget)
        shared_container.setLayout(shared_layout)

        # Add scroll area for shared container
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(shared_container)

        # Create right splitter (for details and preview with scroll)
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(scroll_area)

        # Main layout for Task List and Work File widgets
        task_and_file_layout = QHBoxLayout()
        task_and_file_layout.setContentsMargins(0, 0, 0, 0)
        task_and_file_layout.setSpacing(0)
        task_and_file_layout.addWidget(self.task_list_widget)
        task_and_file_layout.addWidget(self.work_file_widget)

        task_and_file_container = QWidget()
        task_and_file_container.setObjectName("task_and_file_container")
        task_and_file_container.setLayout(task_and_file_layout)

        # Main splitter (horizontal) to hold task_and_file_container and right splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setObjectName("main_splitter")
        main_splitter.addWidget(task_and_file_container)
        main_splitter.addWidget(right_splitter)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([600, 700])

        main_layout.addWidget(top_line)
        main_layout.addWidget(selection_wrapper)
        main_layout.addWidget(main_splitter)
        self.setLayout(main_layout)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    main_window = QTabWidget()
    main_window.setWindowTitle("Work Area")

    # Dummy widgets for demonstration
    selection_widget = QLabel("Selection Widget")
    task_list_widget = QLabel("Task List Widget")
    work_file_widget = QLabel("Work File Widget")
    work_file_detail_widget = QLabel("Work File Detail Widget\n" * 20)  # For scrolling demo
    file_preview_widget = QLabel("File Preview Widget\n" * 20)  # For scrolling demo

    work_area_page = WorkAreaWidget(
        selection_widget, task_list_widget, work_file_widget, work_file_detail_widget, file_preview_widget
    )
    main_window.addTab(work_area_page, "Work Area")

    main_window.show()
    sys.exit(app.exec())
