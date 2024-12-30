from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtGui import QFont


class LineEditComponent(QWidget):
    def __init__(self, id: str, label: str):
        super().__init__()
        self.id = id
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.label = QLabel(label)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.label.setFont(font)
        self.line_edit = QLineEdit()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)
        self.setLayout(self.layout)

    def get_value(self):
        return self.line_edit.text()
