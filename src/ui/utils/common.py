import os

from PySide6.QtWidgets import QLayout, QWidget
from PySide6.QtGui import QFontDatabase, QFont


def set_layout_visibility(layout, state):
    """
    Hide or show all widgets in the given layout.

    Args:
        layout (QLayout): The layout whose widgets should be shown or hidden.
        state (bool): True to show the widgets, False to hide them.

    Raises:
        TypeError: If the provided layout is not a QLayout instance.
    """
    if not isinstance(layout, QLayout):
        raise TypeError(f"Expected a QLayout instance, got {type(layout).__name__} instead.")

    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item.widget():  # If the item is a widget
            item.widget().setVisible(state)
        elif item.layout():  # If the item is another layout
            set_layout_visibility(item.layout(), state)


class CenteringContainer(QWidget):
    """
    A container widget used to center a child widget in the parent table cell.
    """

    def __init__(self, child_widget, parent_table):
        """
        Initialize the CenteringContainer.

        Args:
            child_widget (QWidget): The widget to be centered.
            parent_table (QTableWidget): The parent QTableWidget that manages this container.
        """
        super().__init__()
        logger.debug("CenteringContainer initialized.")

        self.parent_table = parent_table

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(child_widget)

    def mousePressEvent(self, event):
        """
        Forward mouse press events to the parent table.
        """
        logger.debug("CenteringContainer mousePressEvent forwarded to parent table.")
        self.parent_table.mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """
        Forward double-click events to the parent table.
        """
        logger.debug("CenteringContainer mouseDoubleClickEvent forwarded to parent table.")
        self.parent_table.mouseDoubleClickEvent(event)


def load_fonts_from_directory(directory_path):
    """
    Load all font files from the specified directory and its subdirectories.
    """
    font_ids = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith((".ttf", ".otf")):
                font_path = os.path.join(root, file)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    font_ids.append(font_id)
                else:
                    print(f"Failed to load font: {font_path}")
    return font_ids


def verify_fonts(widget):
    """
    Verifies if custom fonts are being used by inspecting QLabel properties.
    """

    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
    font = widget.font()

    available_fonts = QFontDatabase().families()
    print("Available Fonts:", available_fonts)
    print("Font Family:", font.family())
    print("Font Style:", font.style())
    print("Font Weight:", font.weight())
    print("Font Size:", font.pointSize())


def add_indented_item(combo_box, text, indent_width):
    """
    Add an item to the combo box with text indentation.

    :param combo_box: The QComboBox object.
    :param text: The text for the item.
    :param indent_width: The number of spaces for indentation.
    """
    # Use Unicode non-breaking spaces or regular spaces
    indent = "\u00A0" * indent_width  # Non-breaking spaces
    combo_box.addItem(f"{indent}{text}")


def get_widget_size(widget):
    """
    Get the current width and height of the given widget.

    :param widget: The widget whose size is to be retrieved.
    :return: A tuple (width, height) representing the size.
    """
    width = widget.width()
    height = widget.height()
    return width, height


