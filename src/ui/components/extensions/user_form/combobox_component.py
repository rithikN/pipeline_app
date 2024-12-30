from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from PySide6.QtGui import QFont


class ComboBoxComponent(QWidget):
    def __init__(self, id: str, label: str, options: list):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.id = id
        self.label = QLabel(label)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.label.setFont(font)
        self.combo_box = QComboBox()
        self.combo_box.addItems(options)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo_box)

        self.setLayout(self.layout)

    def get_value(self):
        return self.combo_box.currentText()
