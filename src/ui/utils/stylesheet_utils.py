from PySide6.QtCore import QFile, QTextStream
from PySide6.QtWidgets import QWidget


def load_stylesheet(widget: QWidget, stylesheet_file: str):
    stylesheet_path = QFile(stylesheet_file)
    if stylesheet_path.exists():
        stylesheet_path.open(QFile.ReadOnly | QFile.Text)
        stream = QTextStream(stylesheet_path)
        stylesheet = stream.readAll()
        widget.setStyleSheet(stylesheet)
        # Apply the stylesheet content to the widget
    else:
        print(f"Stylesheet not found: {stylesheet_file}")


def setup_tab_styles(tab_widget):
    qss = """
    QTabBar::tab {
        height: 30px;
        width: 75px;
        background: #010409;
        color: #E1E1E8;
        border: 0px solid #010409;
        padding: 5px;
        margin: 0px;
    }
    QTabBar::tab:selected {
        background: #010409;
        font-weight: bold;
    }
    QTabBar::tab:hover {
        background: #010409;
    }
    QTabWidget::pane {
        background: #010409;
        border: 0px solid #444;
        top: -1px;
    }
    """
    tab_widget.setStyleSheet(qss)

