from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QScrollArea, QHBoxLayout, QToolButton
)
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtCore import Qt


class LineEditComponent(QWidget):
    def __init__(self, id: str, label: str, placeholder: str = "", icon_path: str = "", is_password: bool = False):
        super().__init__()
        self.id = id

        # Main layout for this component
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Create and style the label
        self.label = QLabel(label)
        font = QFont()
        font.setPointSize(15)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setFixedHeight(30)

        # Create a container widget to hold both the icon and the QLineEdit
        container = QWidget()
        container.setFixedHeight(48)
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 5, 10, 5)
        container_layout.setSpacing(0)

        # Apply border style to container
        container.setStyleSheet("""
            QWidget {
                border: 1px solid #333;
                border-radius: 5px;
                background-color: white;
            }
        """)

        # Create the QLineEdit
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.setStyleSheet("border: none; background: transparent;")  # Remove QLineEdit border

        if is_password:
            self.line_edit.setEchoMode(QLineEdit.Password)

        # Optionally add an icon to the line edit
        if icon_path:
            pixmap = QPixmap(icon_path)
            if pixmap.isNull():
                print(f"Error: Could not load icon from {icon_path}")
                return

            # Scale the pixmap properly
            scaled_pixmap = pixmap.scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon = QIcon(scaled_pixmap)

            # Create a QToolButton to hold the icon
            self.icon_button = QToolButton()
            self.icon_button.setIcon(icon)
            self.icon_button.setIconSize(scaled_pixmap.size())
            self.icon_button.setStyleSheet("border: none; background: transparent; padding: 5px;")
            self.icon_button.setFixedSize(40, 40)  # Ensure the button size matches the icon

            # Add icon and line_edit to the layout
            container_layout.addWidget(self.icon_button)
            container_layout.addWidget(self.line_edit)

        layout.addWidget(self.label)
        layout.addWidget(container)
        self.setLayout(layout)

    def get_value(self):
        return self.line_edit.text()


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User and Password Form")

        # Create the main layout
        main_layout = QVBoxLayout(self)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setFixedSize(340, 270)
        scroll_area.setWidgetResizable(True)

        # Create a content widget to hold the LineEditComponents
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Add username and password components with placeholders and icons
        username_component = LineEditComponent(
            "username",
            "Enter your username:",
            "User ID",
            icon_path=r"C:\Users\sknay\PycharmProjects\pipeline_app\src\resources\icons\login_page\user.svg"
        )
        password_component = LineEditComponent(
            "password",
            "Enter your password:",
            "••••••••••",
            icon_path=r"C:\Users\sknay\PycharmProjects\pipeline_app\src\resources\icons\login_page\pass.svg"
        )

        # Add components to the content layout
        content_layout.addWidget(username_component)
        content_layout.addWidget(password_component)

        # Set the content widget for the scroll area
        scroll_area.setWidget(content_widget)

        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)


if __name__ == "__main__":
    app = QApplication([])

    # Create and show the main widget
    main_widget = MainWidget()
    main_widget.show()

    app.exec()
