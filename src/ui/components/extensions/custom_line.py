from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor, QPainter, QLinearGradient


class GradientLineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)  # Set the height of the line

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        rect = self.rect()

        # Define the gradient
        gradient = QLinearGradient(rect.topLeft(), rect.topRight())
        gradient.setColorAt(0.49, QColor(255, 255, 255))
        gradient.setColorAt(0.5, QColor(0, 0, 0, 0))

        # Fill the rectangle with the gradient
        painter.fillRect(rect, gradient)
        painter.end()
