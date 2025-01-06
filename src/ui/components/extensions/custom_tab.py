from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QTabBar, QFrame
from PySide6.QtGui import QPainter, QLinearGradient, QColor
from PySide6.QtCore import QRect


class GradientTabBar(QTabBar):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        for index in range(self.count()):
            rect = self.tabRect(index)
            if index == self.currentIndex():
                gradient = QLinearGradient(rect.bottomLeft(), rect.bottomRight())
                gradient.setColorAt(0.39, QColor(0, 0, 0, 0))
                gradient.setColorAt(0.4, QColor(255, 255, 255))
                gradient.setColorAt(0.5, QColor(255, 255, 255))
                gradient.setColorAt(0.6, QColor(255, 255, 255))
                gradient.setColorAt(0.61, QColor(0, 0, 0, 0))

                gradient_rect = QRect(rect.left(), rect.bottom() - 3, rect.width(), 3)
                painter.fillRect(gradient_rect, gradient)


class CustomTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabBar(GradientTabBar())


def create_tab_widget():
    # Main Widget
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)

    main_widget.setStyleSheet(
        """
        background-color:  #2e2e2e;
        """
    )
    # Tab Widget
    tab_widget = CustomTabWidget()
    tab_widget.setTabPosition(QTabWidget.North)
    tab_widget.setStyleSheet(
        """
        QTabBar::tab {
            height: 30px;
            width: 75px;
            background: #2e2e2e;
            color: #E1E1E8;
            border: 0px solid #2e2e2e;
            padding: 5px;
            margin: 0px;
        }
        QTabBar::tab:selected {
            background: #2e2e2e;
            font-weight: bold;
        }
        QTabBar::tab:hover {
            background: #2e2e2e;
        }
        QTabWidget::pane {
            border: 0px solid #444;
            top: -1px;
        }
        """
    )

    # Adding White Line on Top of Tab Content
    top_line = QFrame()
    top_line.setFrameShape(QFrame.HLine)
    top_line.setFrameShadow(QFrame.Plain)
    top_line.setStyleSheet("background-color: #E1E1E8; height: 2px; margin: 0px;")

    # Adding Tabs
    tab_widget.addTab(QWidget(), "Work Area")
    tab_widget.addTab(QWidget(), "Review")

    layout.addWidget(tab_widget)
    layout.addWidget(top_line)
    return main_widget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tab Widget Example")
        self.resize(1200, 800)
        self.setCentralWidget(create_tab_widget())


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
