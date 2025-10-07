"""
work_details_widget.py

UI component for showing work file details.
This widget is now "dumb": it only handles display and emits signals.
All logic (launch, explorer, publish, version-up) is handled in WorkDetailsController.
"""

import os

from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QIcon

from ui.components.forms.details_form import Ui_DetailsForm
from ui.utils.common import set_layout_visibility
from services.constants import SKIP_DATA


class WorkDetailsWidget(QWidget, Ui_DetailsForm):
    # Signals for intent-only communication with controller
    launchRequested = Signal(dict)     # User clicked "Open"
    explorerRequested = Signal(dict)   # User clicked "Explorer"
    publishRequested = Signal(dict)    # User clicked "Publish"
    versionUpDetected = Signal(dict)   # Triggered when version-up happens (controller may rewire monitor)

    def __init__(self, title: str, details_data: dict = None):
        super().__init__()
        self.setupUi(self)

        self._details_data = details_data or {}
        self.details_data_to_be_shown = {}

        # UI setup
        self.image_label = QLabel(self.preview_frame)
        self.image_label.setScaledContents(True)
        self.image_label.setVisible(False)

        self.header_label.setText(title)
        self.details_textEdit.setReadOnly(True)
        self.details_textEdit.setViewportMargins(5, 0, 0, 10)
        set_layout_visibility(self.main_horizontalLayout, False)
        self._update_text_formatting()
        set_layout_visibility(self.main_horizontalLayout, False)
        self.set_image()

        # Buttons setup
        self.explorer_button.setIcon(QIcon("resources/icons/detail_form/explorer.svg"))
        self.explorer_button.setIconSize(QSize(20, 20))
        self.open_button.setIcon(QIcon("resources/icons/detail_form/open.svg"))
        self.open_button.setIconSize(QSize(20, 20))

        # Button connections
        self.open_button.clicked.connect(lambda: self.launchRequested.emit(self._details_data))
        self.explorer_button.clicked.connect(lambda: self.explorerRequested.emit(self._details_data))
        self.publish_file_button.clicked.connect(lambda: self.publishRequested.emit(self._details_data))

    # ---------------------------
    # Data API
    # ---------------------------

    @property
    def details_data(self):
        return self._details_data

    @details_data.setter
    def details_data(self, task_data: dict):
        """Assign new details data and update UI"""
        if not isinstance(task_data, dict):
            raise ValueError("details_data must be a dictionary")

        detail_data = task_data.get("work_detail")
        if not detail_data:
            set_layout_visibility(self.main_horizontalLayout, False)
            return

        self.display_details(task_data)
        self._details_data = task_data
        self.image_label.setVisible(bool(task_data))
        set_layout_visibility(self.main_horizontalLayout, True)

        # just set placeholder image for now
        self.set_image(None)

    # ---------------------------
    # UI Helpers
    # ---------------------------

    def set_preview(self, preview_path: str = None):
        """Set the preview image (called by controller/page)."""
        if preview_path:
            self.set_image(preview_path)
        else:
            self.set_image(None)

    def set_image(self, image_path: str = None):
        """Set preview image or placeholder."""
        placeholder_width, placeholder_height = 138, 132
        placeholder_pixmap = QPixmap(placeholder_width, placeholder_height)
        placeholder_pixmap.fill(Qt.lightGray)

        if not image_path:
            self.image_label.setPixmap(placeholder_pixmap)
            return

        # External image scaling
        external_pixmap = QPixmap(image_path)
        if not external_pixmap.isNull():
            scaled = external_pixmap.scaled(
                placeholder_width, placeholder_height, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            painter = QPainter(placeholder_pixmap)
            x_offset = (placeholder_width - scaled.width()) // 2
            y_offset = (placeholder_height - scaled.height()) // 2
            painter.drawPixmap(x_offset, y_offset, scaled)
            painter.end()

        self.image_label.setPixmap(placeholder_pixmap)

    def display_details(self, details: dict):
        """
        Update the details text with the given dictionary.
        """
        self.details_data_to_be_shown = {key: value for key, value in details.items() if key not in SKIP_DATA}
        self._update_text_formatting()

    def _update_text_formatting(self):
        """
        Render the details text as HTML for the text edit widget.
        """
        html_content = "".join(
            f"<b>{key.upper()}</b>: {value}<br><hr>"
            for key, value in self.details_data_to_be_shown.items()
        )
        self.details_textEdit.setHtml(html_content.rstrip("<hr>"))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_image()

    def _resize_image(self):
        """
        Maintain 16:9 aspect ratio for the image_label.
        """
        frame_width = self.preview_frame.width()
        if frame_width > 0:
            frame_height = int(frame_width * 9 / 16)
            self.image_label.setGeometry(0, 0, frame_width, frame_height)


if __name__ == "__main__":
    # Standalone test
    import sys, logging
    from PySide6.QtWidgets import QApplication
    from pathlib import Path

    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)

    dummy_data = {
        "name": "HL_Sc9998_Sh0040_COMP",
        "work_detail": {
            "file_name": "HL_Sc9998_Sh0040_COMP_v001.ma",
            "work_file": str(Path.home() / "dummy.ma"),
        },
        "dcc_app": {"app_executable_path": "/path/to/maya"},
    }

    widget = WorkDetailsWidget("Work File Details", details_data=dummy_data)
    widget.show()

    sys.exit(app.exec())
