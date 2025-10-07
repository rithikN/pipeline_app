from PySide6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal


class ProgressDialog(QDialog):
    canceled = Signal()  # Signal to notify when the dialog is canceled

    def __init__(self, parent=None, title="Loading", message="Please wait..."):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayout(QVBoxLayout())
        self.setObjectName("progress_dialog")

        # Label for message
        self.label = QLabel(message)
        self.layout().addWidget(self.label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName('progress_bar')
        self.progress_bar.setRange(0, 100)
        self.layout().addWidget(self.progress_bar)

        # Cancel button
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.handle_cancel)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        self.layout().addLayout(button_layout)

        self.setModal(True)
        self._apply_styles()

    def _apply_styles(self):
        self.setStyleSheet(""" ...same stylesheet... """)

    def set_message(self, message: str):
        """Update the dialog message."""
        self.label.setText(message)

    def handle_cancel(self):
        """Emit the canceled signal and close the dialog."""
        self.canceled.emit()
        self.close()

