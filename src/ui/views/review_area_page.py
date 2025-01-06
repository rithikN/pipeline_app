from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QLabel, QListWidget, QFrame
from PySide6.QtCore import Qt
from ui.components.core_widgets.selection import SelectionWidget
from ui.components.extensions.custom_line import GradientLineWidget


class TaskDetailsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        # Placeholder for task details content
        details_label = QLabel("Task Details Placeholder")
        details_label.setStyleSheet("border: 1px solid black; padding: 10px;")
        layout.addWidget(details_label)


class ReviewAreaWidget(QWidget):
    def __init__(self, selection_widget, task_list_widget, task_details_widget):
        super().__init__()
        self.selection_widget = selection_widget
        self.task_list_widget = task_list_widget
        self.task_details_widget = task_details_widget

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

        # Create a parent container for Task List and Task Details
        container_frame = QFrame()
        container_frame.setObjectName(u"MainContainer")
        container_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        container_frame.setLineWidth(1)
        container_layout = QVBoxLayout(container_frame)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Create horizontal splitter for Task List and Task Details
        task_and_details_splitter = QSplitter(Qt.Horizontal)
        task_and_details_splitter.setObjectName("task_and_file_container")
        task_and_details_splitter.addWidget(self.task_list_widget)
        task_and_details_splitter.addWidget(self.task_details_widget)
        task_and_details_splitter.setStretchFactor(0, 1)
        task_and_details_splitter.setStretchFactor(1, 3)

        # Add splitter to container frame
        container_layout.addWidget(task_and_details_splitter)

        main_layout.addWidget(top_line)
        main_layout.addWidget(selection_wrapper)
        main_layout.addWidget(container_frame)

        self.setLayout(main_layout)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Placeholder widgets for TaskListWidget and TaskDetailsWidget
    task_list_widget = QListWidget()  # Replace this with your actual TaskListWidget if available
    task_details_widget = QLabel("Task Details Widget Placeholder")

    review_area = ReviewAreaWidget(SelectionWidget(), task_list_widget, task_details_widget)
    review_area.setWindowTitle("Review Area")
    review_area.show()

    sys.exit(app.exec())
