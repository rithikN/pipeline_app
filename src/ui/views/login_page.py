"""
login_page.py

Defines the LoginPage class which handles user login functionality.
"""

import logging
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QMovie, QFont
from PySide6.QtCore import Qt, QSize

from ui.components.forms.login_form import Ui_LoginForm
from ui.components.extensions.message_box import MessageBox
from ui.utils.stylesheet_loader import load_stylesheet
from ui.utils.common import verify_fonts

from services.data_service import login_user

# Initialize logger
logger = logging.getLogger(__name__)


class LoginPage(QWidget):
    """
    Represents the login page of the 3D Pipeline application.
    """

    def __init__(self, next_page_callback=None):
        """
        Initialize the LoginPage widget.

        Args:
            next_page_callback (callable, optional):
                A callback function to navigate to the next page upon successful login.
        """
        super().__init__()
        logger.info("Initializing LoginPage...")

        self.next_page_callback = next_page_callback
        self.message_box = MessageBox()
        self.login_ui = Ui_LoginForm()
        self.username = ""

        self._setup_ui()
        self._setup_connections()

        verify_fonts(self.login_ui.username_label)

    def _setup_ui(self):
        """
        Set up the UI elements and styles for the login page.
        """
        logger.debug("Setting up UI for LoginPage.")
        self.setObjectName("login_page")

        # Load the UI from the generated Qt Designer form
        self.login_ui.setupUi(self)

        # Load and apply the login stylesheet
        load_stylesheet(self, r'ui\stylesheets\login_style.css')

        # Set up the GIF animation
        movie = QMovie("resources/logo.gif")
        self.login_ui.Welcome_label.setMovie(movie)
        movie.start()

        # Center the GIF label
        self.login_ui.Welcome_label.setAlignment(Qt.AlignCenter)

    def _setup_connections(self):
        """
        Connect signals to slots for handling user actions.
        """
        logger.debug("Setting up connections for LoginPage.")
        self.login_ui.login_pushButton.clicked.connect(self._on_login)

    def _on_login(self):
        """
        Handle the login process when the user clicks the "Login" button.
        """
        logger.debug("Login button clicked. Attempting to authenticate user.")
        self.username = self.login_ui.username_lineEdit.text()
        password = self.login_ui.password_lineEdit.text()

        if not self.username or not password:
            logger.warning("Username or password not provided. Showing warning message.")
            self.message_box.show_message(
                "Please enter both username and password.",
                message_type="warning",
                title="Input Error"
            )
            return

        response = login_user({"username": self.username, "password": password})
        if not response:
            logger.error("No response received from the login service.")
            return

        print(self.login_ui.outside_horizontalSpacer_1.geometry())
        rect = self.login_ui.outside_horizontalSpacer_1.geometry()
        width = rect.width()
        height = rect.height()
        print('inside_verticalSpacer_5', self.login_ui.inside_verticalSpacer_5.geometry().width(),
              self.login_ui.inside_verticalSpacer_5.geometry().height())
        print('inside_verticalSpacer_1', self.login_ui.inside_verticalSpacer_1.geometry().width(),
              self.login_ui.inside_verticalSpacer_1.geometry().height())
        print('inside_verticalSpacer_3', self.login_ui.inside_verticalSpacer_3.geometry().width(),
              self.login_ui.inside_verticalSpacer_3.geometry().height())
        print('inside_verticalSpacer_4', self.login_ui.inside_verticalSpacer_4.geometry().width(),
              self.login_ui.inside_verticalSpacer_4.geometry().height())
        print(f"Spacer width: {width}, height: {height}")

        print(self.login_ui.login_frame.height(), '>>>')
        if response.get("status") == "success":
            logger.info(f"User '{self.username}' logged in successfully.")
            if self.next_page_callback:
                self.next_page_callback()
        else:
            logger.warning(f"Login failed for user '{self.username}'.")
            self.message_box.show_message(
                "Login failed. Please check your credentials and try again.",
                message_type="warning",
                title="Login Failed"
            )

    def get_username(self):
        """
        Return the username entered by the user.

        Returns:
            str: The username.
        """
        return self.username

    def resizeEvent(self, event):
        """
        Dynamically adjust the Welcome_label width on window resize.

        Args:
            event (QResizeEvent): The resize event object.
        """
        total_width = self.width()
        label_width = total_width // 2
        self.login_ui.Welcome_label.setFixedWidth(label_width)
        self.login_ui.Welcome_label.setMaximumSize(QSize(label_width, self.height()))
        super().resizeEvent(event)


from PySide6.QtGui import QFont


def apply_global_font(widget, font_name):
    font = QFont(font_name)
    widget.setFont(font)
    for child in widget.findChildren(QWidget):
        child.setFont(font)


if __name__ == "__main__":
    # Setup application and logger
    from PySide6.QtWidgets import QApplication
    import sys

    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    from PySide6.QtGui import QFontDatabase, QFont

    font_id_inter = QFontDatabase.addApplicationFont(
        r"C:\Users\sknay\PycharmProjects\pipeline_app\src\resources\fonts\Inter\Inter-VariableFont_opsz,wght.ttf")
    if font_id_inter != -1:
        families = QFontDatabase.applicationFontFamilies(font_id_inter)
        print("Loaded Font Families for Inter:", families)
    else:
        print("Failed to load the Inter font.")
    # Create and show the LoginPage
    login_page = LoginPage()
    # apply_global_font(login_page, "Inter")
    login_page.show()

    # Start the application event loop
    sys.exit(app.exec())
