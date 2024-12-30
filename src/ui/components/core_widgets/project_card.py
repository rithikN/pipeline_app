"""
project_card.py

Defines the ProjectCard widget, which displays project information
(title, type, and optional thumbnail image).
"""

import logging
import sys
from typing import Optional

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt

from ui.components.forms.project_card_form import Ui_ProjectCard

# Initialize logger (optional; configure as needed in your main application)
logger = logging.getLogger(__name__)


class ProjectCard(QWidget):
    """
    A widget representing a card that displays project information,
    including a title, project type, and a thumbnail image.
    """

    def __init__(
            self,
            title: str,
            project_type: str,
            thumbnail: Optional[str] = None,
            parent: Optional[QWidget] = None
    ):
        """
        Initialize the ProjectCard.

        Args:
            title (str): The title of the project.
            project_type (str): The project type (e.g., 'VFX', 'Animation').
            thumbnail (str, optional): Path to a thumbnail image file. Defaults to None.
            parent (QWidget, optional): The parent widget, if any. Defaults to None.
        """
        super().__init__(parent)
        logger.debug("Initializing ProjectCard widget.")

        # Instantiate the auto-generated UI
        self._ui = Ui_ProjectCard()
        self._ui.setupUi(self)

        # Keep local references for display logic
        self._title = title
        self._project_type = project_type
        self._thumbnail = thumbnail

        # Fix widget size
        self.setFixedSize(250, 180)

        # Apply styles
        self._apply_styles()

        # Populate widget fields
        self._populate_fields()

    def _apply_styles(self):
        """
        Apply the stylesheet for this widget and its child elements.
        """
        logger.debug("Applying styles to ProjectCard.")
        self.setStyleSheet(
            """
            QWidget {
                background-color: #B6C6DC;
            }
            QLabel {
                color: #000000;
            }
            QLabel#titleLabel {
                background-color: #E1E1E8;
                font-size: 14px;
                font-weight: bold;
                color: #002855;
                text-align: center;
            }
            QLabel#authorLabel {
                background-color: #E1E1E8;
                font-size: 12px;
                color: #333333; /* Gray */
                text-align: top;
            }
            QLabel#emptyLabel {
                background-color: #E1E1E8;
                font-size: 12px;
                color: #333333; /* Gray */
                text-align: top;
            }
            QLabel#thumbnailLabel {
                background-color: #B6C6DC;
                border: 1px solid #A0A0A0;
                min-height: 100px;
                text-align: center;
            }
            """
        )

    def _populate_fields(self):
        """
        Populate label fields and thumbnail based on the provided parameters.
        """
        logger.debug(
            f"Populating fields: title={self._title}, "
            f"project_type={self._project_type}, thumbnail={self._thumbnail}"
        )

        # Title
        self._ui.titleLabel.setText(self._title.upper())

        # Project type
        self._ui.authorLabel.setText(f"PRJ   {self._project_type.title()}")

        # Handle thumbnail display
        if self._thumbnail:
            pixmap = QPixmap(self._thumbnail)
            scaled_pixmap = pixmap.scaled(
                self._ui.thumbnailLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self._ui.thumbnailLabel.setPixmap(scaled_pixmap)
            self._ui.thumbnailLabel.setAlignment(Qt.AlignCenter)
        else:
            self._ui.thumbnailLabel.setText("No Thumbnail")
            self._ui.thumbnailLabel.setAlignment(Qt.AlignCenter)

            # Style "No Thumbnail" text
            font = QFont()
            font.setItalic(True)
            font.setPointSize(10)
            self._ui.thumbnailLabel.setFont(font)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)

    # Example usage of ProjectCard with parent=None
    widget = ProjectCard(
        title="projectA",
        project_type="VFX",
        thumbnail="path/to/your_thumbnail.png",
        parent=None  # or pass another QWidget if desired
    )
    widget.show()

    sys.exit(app.exec())
