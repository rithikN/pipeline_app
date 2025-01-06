from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QScrollArea,
)
from PySide6.QtGui import QFont, QIcon, QAction, QPixmap
from PySide6.QtCore import Qt


class LineEditComponent(QWidget):
    def __init__(self, id: str, label: str, placeholder: str = "", icon_path: str = "", is_password: bool = False):
        super().__init__()
        self.id = id

        # Main layout for this component
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create and style the label
        self.label = QLabel(label)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setFixedHeight(30)

        # Create and style the line edit
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText(placeholder)

        if is_password:
            self.line_edit.setEchoMode(QLineEdit.Password)

        # Optionally add an icon to the line edit
        if icon_path:
            # Add icon with increased size
            if icon_path:
                pixmap = QPixmap(icon_path)
                if pixmap.isNull():
                    print(f"Error: Could not load icon from {icon_path}")
                    return

                # Scale the pixmap only by height, maintaining the width proportion
                scaled_pixmap = pixmap.scaledToHeight(
                    40,  # Icon height slightly smaller than the QLineEdit height
                    Qt.SmoothTransformation,
                )
            icon = QIcon(scaled_pixmap)
            action = QAction(icon, "", self.line_edit)
            action.setIconVisibleInMenu(False)  # Hide in menus (optional)
            action.setIcon(icon)
            self.line_edit.addAction(action, QLineEdit.LeadingPosition)

        # Add widgets to layout
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)

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
            icon_path=r"path/to/user_icon.png"
        )
        password_component = LineEditComponent(
            "password",
            "Enter your password:",
            "••••••••••",
            icon_path=r"C:\Users\sknay\Downloads\icons_user\user_icon.png"
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
