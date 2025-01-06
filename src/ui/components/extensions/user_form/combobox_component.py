from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QApplication
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt


class ComboBoxComponent(QWidget):
    def __init__(self, id: str, label: str, options: list, icon_path: str = None):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.id = id
        self.icon_path = icon_path

        # Create and style the label
        self.label = QLabel(label)
        self.label.setFixedHeight(30)
        self.label.setStyleSheet("font-size: 13px; font-weight: bold;")

        # Create the combo box with icon
        self.combo_box_layout = QHBoxLayout()
        self.combo_box_layout.setContentsMargins(0, 0, 0, 0)
        self.combo_box_layout.setSpacing(5)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(30, 30)  # Reserve space for the icon
        self.icon_label.setStyleSheet("background: transparent;")

        self.combo_box = QComboBox()
        self.combo_box.addItems(options)

        # Add widgets to layout based on the icon
        if self.icon_path:
            if self._set_icon():  # Only add the icon label if the icon is valid
                self.combo_box_layout.addWidget(self.icon_label)
        self.combo_box_layout.addWidget(self.combo_box)

        self.layout.addWidget(self.label)
        self.layout.addLayout(self.combo_box_layout)

        self.setLayout(self.layout)

    def _set_icon(self):
        """Load and set the SVG icon."""
        pixmap = self._load_svg_as_pixmap(self.icon_path, 30)

        if pixmap is None:
            print(f"Error: Could not load SVG icon from {self.icon_path}")
            return False

        self.icon_label.setPixmap(pixmap)
        return True

    def _load_svg_as_pixmap(self, svg_path, size):
        """Render an SVG file as a QPixmap of the given size."""
        renderer = QSvgRenderer(svg_path)
        if not renderer.isValid():
            print(f"Error: Invalid SVG file at {svg_path}")
            return None

        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return pixmap

    def get_value(self):
        return self.combo_box.currentText()


# Example Usage
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    main_widget = QWidget()
    main_layout = QVBoxLayout(main_widget)

    # Add ComboBoxComponent with an SVG icon
    combo_box_with_icon = ComboBoxComponent(
        id="example1",
        label="With Icon:",
        options=["Option 1", "Option 2", "Option 3"],
        icon_path=r"C:\Users\sknay\Downloads\icons_user\icon _ user _ user.svg",  # Replace with actual SVG path
    )

    # Add ComboBoxComponent without an icon
    combo_box_without_icon = ComboBoxComponent(
        id="example2",
        label="Without Icon:",
        options=["Option A", "Option B", "Option C"],
        icon_path=None,  # No icon
    )

    main_layout.addWidget(combo_box_with_icon)
    main_layout.addWidget(combo_box_without_icon)

    main_widget.setWindowTitle("ComboBox with and without Icon")
    main_widget.setFixedSize(400, 300)
    main_widget.show()

    sys.exit(app.exec())
