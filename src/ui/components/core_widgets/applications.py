#!/usr/bin/env python3
import sys
import subprocess
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout,
                               QScrollArea, QSizePolicy, QMainWindow)
from PySide6.QtCore import Qt, QSize
APPLICATIONS = [
    {
        "name": "Maya",
        "icon": r"C:\Program Files\Autodesk\Maya2023\icons\mayaPlaceholder.png",
        "command": r"C:\Program Files\Autodesk\Maya2023\bin\maya.exe"
    },
    {
        "name": "Nuke",
        "icon": r"C:\Program Files\Nuke14.0v1\plugins\icons\NukeApp64.png",
        "command": r"C:\Program Files\Nuke14.0v1\Nuke14.0.exe"
    },
    {
        "name": "Silhouette",
        "icon": r"C:\Program Files\BorisFX\Silhouette 2021.5\application.ico",
        "command": r"C:\Program Files\BorisFX\Silhouette 2021.5\Silhouette.exe"
    }
]

class ApplicationIcon(QWidget):
    def __init__(self, application):
        super().__init__()
        self.application = application
        self.name = self.application['name']
        self.command = self.application['command']
        self.icon = self.application['icon']
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        self.icon_size = QSize(32, 32)
        self.icon_label = QLabel(self)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setPixmap(QPixmap(self.icon).scaled(self.icon_size.width(), self.icon_size.height(),
                                                            Qt.AspectRatioMode.KeepAspectRatio,
                                                            Qt.TransformationMode.SmoothTransformation))
        self.name_label = QLabel(self.name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.name_label)
        self.setStyleSheet("""
            ApplicationIcon {
                border: 1px solid transparent;
                border-radius: 5px;
            }
            ApplicationIcon:hover {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            subprocess.call(self.command, shell=True)
            event.accept()
        else:
            super().mousePressEvent(event)

class ApplicationsWidget(QWidget):
    def __init__(self, applications):
        super().__init__()
        self.applications = applications
        self.setWindowTitle("Application Launcher")
        self.setGeometry(100, 100, 180, 60)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(15)
        self.populate_grid()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.grid_container)
        self.main_layout.addWidget(self.scroll_area)
        self.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        while self.grid_layout.count() > 0:
            item = self.grid_layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        self.populate_grid()

    def populate_grid(self):
        target_icon_width = 100
        num_columns = max(1, (self.width() - target_icon_width) // 2)
        row = 0
        column = 0
        for application in self.applications:
            icon_widget = ApplicationIcon(application)
            self.grid_layout.addWidget(icon_widget, row, column)
            column += 1
            if column >= num_columns:
                column = 0
                row += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = ApplicationsWidget(applications=APPLICATIONS)
    sys.exit(app.exec())
