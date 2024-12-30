"""
menu_widget.py

Demonstrates a custom widget (CustomMenuWidget) that can be embedded
in a QMenuBar corner widget. Includes a main window example
to illustrate usage.
"""

import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QHBoxLayout,
    QFrame, QMenuBar, QMenu, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt

# Initialize logger (optional)
logger = logging.getLogger(__name__)


class CustomMenuWidget(QWidget):
    """
    A custom widget meant to be displayed in a QMenuBar corner.
    Displays a circular icon and a text label.
    """

    def __init__(self, text=None, parent=None):
        """
        Initialize the CustomMenuWidget.

        Args:
            text (str, optional): The text to display. Defaults to None.
        """
        super().__init__(parent)
        logger.debug("Initializing CustomMenuWidget.")

        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        # Frame for White Border
        self._frame = QFrame()
        self._frame.setFrameShape(QFrame.Shape.StyledPanel)
        self._frame.setStyleSheet("""
            QFrame {
                border: 1px solid #E1E1E8;
                border-radius: 10px;
                background-color: black;
            }
        """)
        frame_layout = QHBoxLayout(self._frame)
        frame_layout.setContentsMargins(5, 5, 5, 5)
        frame_layout.setSpacing(5)

        # Circular Icon
        self._icon_label = QLabel()
        self._icon_label.setFixedSize(24, 24)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setStyleSheet("""
            QLabel {
                border-radius: 12px;
                background-color: #E1E1E8;
                color: black;
                font-size: 12px;
                font-weight: bold;
            }
        """)

        # Text Label
        self._text_label = QLabel()
        self._text_label.setStyleSheet("""
            color: #E1E1E8; 
            font-size: 14px; 
            font-weight: bold; 
            background-color: transparent; 
            border: none; 
        """)

        # Add widgets to frame layout
        frame_layout.addWidget(self._icon_label)
        frame_layout.addWidget(self._text_label)

        # Add frame to main layout
        self._main_layout.addWidget(self._frame)

        # Initialize widget with provided text
        self.set_text(text)

    def set_text(self, text: str):
        """
        Set the text and update the icon's initial character.

        Args:
            text (str): The text to display in the widget.
        """
        logger.debug(f"Setting text for CustomMenuWidget: {text}")
        if text:
            self._icon_label.setText(text[0])
            self._text_label.setText(text)
        else:
            self._icon_label.clear()
            self._text_label.clear()


class MainWindow(QMainWindow):
    """
    Example main window that demonstrates using the CustomMenuWidget
    as a corner widget in the QMenuBar.
    """

    def __init__(self):
        """
        Initialize the main window.
        """
        super().__init__()
        logger.info("Initializing MainWindow with custom menu widget demo.")
        self.setWindowTitle("Custom Widget in Menu Bar")
        self.resize(800, 500)

        self._setup_menu_bar()

    def _setup_menu_bar(self):
        """
        Configure the menu bar and add the custom widgets in the corner.
        """
        logger.debug("Setting up menu bar.")
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Add standard menus
        file_menu = menu_bar.addMenu("File")
        edit_menu = menu_bar.addMenu("Edit")

        # Style the menu bar for vertical centering
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #222; /* Dark background */
                color: #E1E1E8;
                padding: 5px; /* Adjust padding for vertical alignment */
            }
            QMenuBar::item {
                background-color: transparent;
                margin: 3px 10px; /* Adjust margin for vertical centering */
                padding: 10px 10px;
            }
            QMenuBar::item:selected {
                background-color: #444; /* Highlight color when hovered */
            }
            QMenu {
                background-color: #333; /* Drop-down menu background */
                color: #E1E1E8;
            }
        """)

        # Create a corner widget container
        corner_widget = QWidget()
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 10, 0)  # Right margin
        corner_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Spacer to push the custom widgets to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        corner_layout.addWidget(spacer)

        # Create project and user widgets
        project_widget = CustomMenuWidget("Project")
        user_widget = CustomMenuWidget("Admin")

        # Add custom widgets
        corner_layout.addWidget(project_widget)
        corner_layout.addWidget(user_widget)

        # Optional: Add extra space at the right end
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        right_spacer.setFixedWidth(100)
        corner_layout.addWidget(right_spacer)

        # Assign the corner widget to top-right corner
        menu_bar.setCornerWidget(corner_widget, Qt.Corner.TopRightCorner)


if __name__ == "__main__":
    # Configure logging (optional)
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    window = MainWindow()
    project_widget = CustomMenuWidget("Project")
    window.show()
    sys.exit(app.exec())
