from PySide6.QtCore import QFile, QTextStream
from PySide6.QtWidgets import QWidget


def load_stylesheet(widget: QWidget, stylesheet_file: str):
    stylesheet_path = QFile(stylesheet_file)
    if stylesheet_path.exists():
        stylesheet_path.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(stylesheet_path)
        stylesheet = stream.readAll()
        widget.setStyleSheet(stylesheet)  # Apply the stylesheet content to the widget
    else:
        print(f"Stylesheet not found: {stylesheet_file}")
