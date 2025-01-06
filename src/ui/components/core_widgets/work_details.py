from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QIcon
from ui.components.forms.details_form import Ui_DetailsForm  # The auto-generated UI
from ui.components.extensions.message_box import MessageBox

from ui.utils.common import set_layout_visibility
from services.constants import PREVIEW_PATH


class WorkDetailsWidget(QWidget, Ui_DetailsForm):
    # Signal to allow external components to trigger updates
    trigger_update = Signal(dict)

    def __init__(self, title, details_data=None):
        super().__init__()
        self.setupUi(self)  # Set up the UI from the .ui file

        # Create the image_label inside the preview_frame
        self.image_label = QLabel(self.preview_frame)
        self.image_label.setScaledContents(True)
        self.image_label.setVisible(False)

        self.message_box = MessageBox()
        self._details_data = details_data if details_data else {}

        self.header_label.setText(title)
        self.details_textEdit.setReadOnly(True)
        self.details_textEdit.setViewportMargins(5, 0, 0, 10)
        self._update_text_edit()

        set_layout_visibility(self.main_horizontalLayout, False)

        # Set a placeholder image with 16:9 aspect ratio
        self.set_image()

        self.delete_button.setIcon(QIcon("resources/icons/detail_form/delete.svg"))
        self.delete_button.setIconSize(QSize(20, 20))
        self.explorer_button.setIcon(QIcon("resources/icons/detail_form/explorer.svg"))
        self.explorer_button.setIconSize(QSize(20, 20))
        self.open_button.setIcon(QIcon("resources/icons/detail_form/open.svg"))
        self.open_button.setIconSize(QSize(20, 20))

        self.delete_button.clicked.connect(
            lambda: self.message_box.show_message(
                "Yet To Implement",
                message_type="info",
                title="delete button selected"
            )
        )
        self.explorer_button.clicked.connect(
            lambda: self.message_box.show_message(
                "Yet To Implement",
                message_type="info",
                title="explorer button selected"
            )
        )
        self.open_button.clicked.connect(
            lambda: self.message_box.show_message(
                "Yet To Implement",
                message_type="info",
                title="open button selected"
            )
        )

    def set_image(self, image_path=None):
        """
        Load an external image into a QPixmap, fit it into a 16:9 placeholder,
        and set it to a QLabel.

        :param image_path: Path to the external image.
        :param label: QLabel to display the image.
        """
        # Desired placeholder size (16:9 aspect ratio)
        placeholder_width = 238
        placeholder_height = 132

        # Create a placeholder pixmap with light gray background
        placeholder_pixmap = QPixmap(placeholder_width, placeholder_height)
        placeholder_pixmap.fill(Qt.lightGray)

        if not image_path:
            return
        # Load the external image
        external_pixmap = QPixmap(image_path)

        if not external_pixmap.isNull():  # Check if the image is loaded successfully
            # Scale the external image to fit within the placeholder while maintaining aspect ratio
            scaled_pixmap = external_pixmap.scaled(
                placeholder_width, placeholder_height,
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )

            # Center the scaled image onto the placeholder using QPainter
            painter = QPainter(placeholder_pixmap)
            x_offset = (placeholder_width - scaled_pixmap.width()) // 2
            y_offset = (placeholder_height - scaled_pixmap.height()) // 2
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
            painter.end()

        self.image_label.setPixmap(placeholder_pixmap)

    @property
    def details_data(self):
        return self._details_data

    @details_data.setter
    def details_data(self, data):
        if isinstance(data, dict):
            if not data:
                set_layout_visibility(self.main_horizontalLayout, False)
                return

            self.update_details(data)
            self.image_label.setVisible(bool(data))
            set_layout_visibility(self.main_horizontalLayout, True)
            self.set_image(data.get(PREVIEW_PATH))
        else:
            raise ValueError("details_data must be a dictionary")

    def update_details(self, details):
        """
        Update the details text with the given dictionary.
        """
        self._details_data = details
        self._update_text_edit()

    def _update_text_edit(self):
        new_text = "\n".join(
            f"{key}: {value}" for key, value in self._details_data.items()
        )
        self.details_textEdit.setText(new_text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._resize_image()

    def _resize_image(self):
        """Maintain 16:9 aspect ratio for the image_label based on preview_frame's width."""
        frame_width = self.preview_frame.width()
        if frame_width > 0:
            frame_height = int(frame_width * 9 / 16)
            # Position the image_label within the preview_frame
            self.image_label.setGeometry(0, 0, frame_width, frame_height)
            print(frame_width, frame_height)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    widget = WorkDetailsWidget('testing')
    widget.show()

    # Example dynamic update after the widget is shown
    widget.details_data = {
        "File Name": "prj_e001_sq001_sh0001_dept_v001.ext\n",
        "File Type": "Maya / .ma",
        "File Size": "620.40 MB",
        "Last Saved": "01-02-2024 10:30",
        "Lock Status": "Unlocked",
        'preview_path': 'path.jpeg'
    }

    sys.exit(app.exec())
