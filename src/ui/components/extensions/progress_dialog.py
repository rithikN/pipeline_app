from PySide6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal


class ProgressDialog(QDialog):
    canceled = Signal()  # Signal to notify when the dialog is canceled

    def __init__(self, parent=None, title="Loading", message="Please wait..."):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLayout(QVBoxLayout())
        self.setObjectName("progress_dialog")

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName('progress_bar')
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.layout().addWidget(QLabel(message))
        self.layout().addWidget(self.progress_bar)

        # Cancel button
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.setEnabled(False)
        cancel_button.clicked.connect(self.handle_cancel)
        button_layout.addStretch()  # Push the button to the right
        button_layout.addWidget(cancel_button)
        self.layout().addLayout(button_layout)

        self.setModal(True)

        # Apply styles
        self.setStyleSheet("""
            QDialog#progress_dialog {
                background-color: #E1E1E8;  /* Light grayish blue */
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                background-color: #E1E1E8;
                color: #000000;  /* Black text */
                font-size: 14px;
            }
            QProgressBar {
                border: 1px solid #B0B0B0; /* Light gray border */
                background: #FFFFFF;       /* White background */
                height: 20px;              /* Fixed height */
                border-radius: 10px;
                text-align: center;        /* Center the text inside the progress bar */
            }
            QProgressBar::chunk {
                background-color: #4C72B0; /* Blue progress color */
                border-radius: 10px;
            }
            QPushButton#cancel_button {
                background-color: #4C72B0; /* Blue button */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton#cancel_button:hover {
                background-color: #3b5998; /* Darker blue on hover */
            }
            QPushButton#cancel_button:disabled {
                background-color: #B0B0B0; /* Gray when disabled */
                color: #FFFFFF;
            }
        """)

    def handle_cancel(self):
        """Emit the canceled signal and close the dialog."""
        self.canceled.emit()
        self.close()
