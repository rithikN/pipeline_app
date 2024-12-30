# ui/components/input_field.py
from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QLabel


class InputField(QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.label = label
        self.init_ui()

    def init_ui(self):
        self.label_widget = QLabel(self.label, self)
        self.input_widget = QLineEdit(self)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label_widget)
        layout.addWidget(self.input_widget)

        self.setLayout(layout)
