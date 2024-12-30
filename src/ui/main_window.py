"""
main_window.py

Provides the MainWindow class for the 3D Pipeline application.
This class handles navigation between different pages and manages
the top bar (menu bar) via TopBarManager.
"""

import logging
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QWidget,
    QHBoxLayout,
    QMenuBar
)

from ui.components.core_widgets.menu_widget import CustomMenuWidget
from ui.components.extensions.message_box import MessageBox

from ui.managers.menu_manager import TopBarManager
from ui.managers.signal_manager import SignalManager

from ui.views.login_page import LoginPage
from ui.views.form_page import FormPage
from ui.views.project_page import ProjectPage
from ui.views.task_mancer_page import TaskMancerPage

from services.constants import ABOUT_INFO_LABEL, ABOUT_LABEL

# Initialize logger
logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main window of the 3D Pipeline application. This window manages
    multiple pages (login, form, project, task mancer) using a QStackedWidget
    and handles dynamic menu bar widgets.

    Attributes:
        message_box (MessageBox): Custom message box for displaying alerts/info.
        form_data (dict): Data collected from FormPage.
        project_data (dict): Data collected from ProjectPage.
        menu_widget (QWidget): A corner widget for displaying user/project info in the menu bar.
        menu_layout (QHBoxLayout): The layout for the corner widget.
        user_menu (QAction): The user menu object in the menu bar.
        project_menu (QAction): The project menu object in the menu bar.
        display_user_widget (CustomMenuWidget): Widget to display username info in the corner.
        display_project_widget (CustomMenuWidget): Widget to display project info in the corner.
        login_page (LoginPage): The login page view.
        form_page (FormPage): The form page view.
        project_page (ProjectPage): The project page view.
        task_mancer_page (TaskMancerPage): The task mancer page view.
        stack (QStackedWidget): The container that holds all pages and manages page navigation.
        menu_bar (QMenuBar): The main menu bar of the application.
    """

    def __init__(self):
        """
        Initialize the MainWindow class, set up the UI, pages, and menu bar.
        """
        super().__init__()
        self.setWindowTitle("3D Pipeline")
        self.resize(1200, 700)

        # Logging an informational message
        logger.info("Initializing MainWindow...")

        # -- Initialize message box & data containers --
        self.message_box = MessageBox()
        self.signal_manager = SignalManager()
        self.form_data = {}
        self.project_data = {}

        self.menu_widget = None
        self.menu_layout = None
        self.user_menu = None
        self.project_menu = None
        self.display_user_widget = None
        self.display_project_widget = None

        # -- Initialize pages --
        self.login_page = LoginPage(next_page_callback=self.show_form_page)
        self.form_page = FormPage(
            next_page_callback=self.show_project_page,
            prev_page_callback=self.go_back_to_login_page
        )
        self.project_page = ProjectPage(
            next_page_callback=self.show_task_mancer_page,
            prev_page_callback=self.go_back_to_form_page
        )
        self.task_mancer_page = TaskMancerPage(
            prev_page_callback=self.go_back_to_project_page
        )

        # -- Create and configure the stacked widget --
        self.stack = QStackedWidget()
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.form_page)
        self.stack.addWidget(self.project_page)
        self.stack.addWidget(self.project_page)
        self.stack.addWidget(self.task_mancer_page)
        self.setCentralWidget(self.stack)

        # -- Create top bar manager --
        self.top_bar_manager = TopBarManager(self.menuBar(), self.message_box, self.signal_manager)

        # -- Connect signals to slots --
        self._connect_signals()

        # --- Example usage for quick testing ---
        # self.login_page.username = 'test user'
        # self.show_task_mancer_page({'project_name': 'Testing Project'})
        # self.show_form_page()
        # ---------------------------------------

        logger.info("MainWindow initialized successfully.")

    # --------------------
    # Signal Connections
    # --------------------

    def _connect_signals(self):
        """
        Connect SignalManager signals to appropriate slots.
        """
        logger.debug("Connecting SignalManager signals to MainWindow slots.")

        # Application-wide signals
        self.signal_manager.update_triggered.connect(self.handle_update_app)
        self.signal_manager.exit_triggered.connect(self.close)
        self.signal_manager.about_triggered.connect(self.show_about_dialog)
        self.signal_manager.wiki_triggered.connect(self.show_wiki)

        # User-related signals
        self.signal_manager.edit_triggered.connect(self.handle_edit_user)
        self.signal_manager.logout_triggered.connect(self.handle_logout)

        # Project-related signals
        self.signal_manager.download_triggered.connect(self.task_mancer_page._download_project_files)
        self.signal_manager.exit_project_triggered.connect(self.task_mancer_page._on_previous)

    # --------------------
    # Slot Implementations
    # --------------------

    def handle_update_app(self):
        """
        Handle the 'Update App' action from the menu.
        """
        logger.info("Handling 'Update App' action.")
        self.message_box.show_info('Update functionality is not implemented yet.', 'Update')

    def show_about_dialog(self):
        """
        Display an 'About' dialog.
        """
        logger.info("Showing 'About' dialog.")
        self.message_box.show_info(ABOUT_INFO_LABEL, ABOUT_LABEL)

    def show_wiki(self):
        """
        Handle the 'Wiki' menu action.
        """
        logger.info("Showing 'Wiki' page.")
        # Implement wiki page display or open browser
        self.message_box.show_info('Wiki functionality is not implemented yet.', 'Wiki')

    def handle_edit_user(self):
        """
        Handle the 'Edit User' action.
        """
        logger.info("Handling 'Edit User' action.")
        # Implement user editing functionality
        self.message_box.show_info('Edit User functionality is not implemented yet.', 'Edit User')

    def handle_logout(self):
        """
        Handle the 'Logout' action.
        """
        logger.info("Handling 'Logout' action.")
        # Implement logout functionality
        self.message_box.show_info('Logout', 'Logging out...')
        self.go_back_to_login_page()

    # --------------------
    # Navigation Methods
    # --------------------

    def show_form_page(self):
        """
        Navigate from login -> form page.
        Remove any corner widget, remove any existing 'Project' section,
        add a 'User' section, then switch to FormPage.
        """
        logger.debug("Navigating to FormPage.")
        # Remove top bar corner widget and project section if any
        self.top_bar_manager.remove_topbar_widget()
        self.top_bar_manager.remove_project_section()

        # Set username in form page
        username = self.login_page.get_username()
        self.form_page.set_username(username)

        # Add the 'User' section and go to FormPage
        self.top_bar_manager.add_user_section()
        self.stack.setCurrentWidget(self.form_page)

    def show_project_page(self, form_data):
        """
        Navigate from form page -> project page.
        Remove any top bar widget, add a new corner widget with username,
        remove 'Project' section if it exists, then switch to ProjectPage.

        Args:
            form_data (dict): Form data collected from FormPage.
        """
        logger.debug("Navigating to ProjectPage.")
        self.form_data = form_data

        # Remove top bar corner widget
        self.top_bar_manager.remove_topbar_widget()

        # Show a corner widget with just the username
        username = self.login_page.get_username()
        self.top_bar_manager.add_topbar_widget(parent=self, username=username)

        # Remove project section if previously added
        self.top_bar_manager.remove_project_section()

        # Set form data on ProjectPage
        self.project_page.set_form_data(form_data)
        self.stack.setCurrentWidget(self.project_page)

    def show_task_mancer_page(self, project_data):
        """
        Navigate from project page -> task mancer page.
        Remove any top bar widget, add a new one with username + project name,
        add 'Project' section to the top bar, then switch to TaskMancerPage.

        Args:
            project_data (dict): Project data collected from ProjectPage.
        """
        logger.debug("Navigating to TaskMancerPage.")
        self.project_data = project_data

        # Reset corner widget
        self.top_bar_manager.remove_topbar_widget()

        # Add new corner widget with user + project
        username = self.login_page.get_username()
        project_name = project_data.get("project_name", "Unknown Project")
        self.top_bar_manager.add_topbar_widget(self, username=username, project_name=project_name)

        # Add the 'Project' section
        self.top_bar_manager.add_project_section()

        # Set project data on TaskMancerPage and switch
        self.task_mancer_page.set_project(project_name)
        self.stack.setCurrentWidget(self.task_mancer_page)

    # --------------------
    # Back Navigation
    # --------------------

    def go_back_to_form_page(self):
        """
        Navigate from project page -> form page (triggered by 'Back' in ProjectPage).
        """
        logger.debug("Navigating back to FormPage.")
        self.stack.setCurrentWidget(self.form_page)

    def go_back_to_project_page(self):
        """
        Navigate from task mancer page -> project page (triggered by 'Back' in TaskMancerPage).
        """
        logger.debug("Navigating back to ProjectPage.")
        self.top_bar_manager.remove_project_section()
        self.show_project_page(self.form_data)

    def go_back_to_login_page(self):
        """
        Navigate from form page -> login page (triggered by 'Back' in FormPage).
        """
        logger.debug("Navigating back to LoginPage.")
        self.stack.setCurrentWidget(self.login_page)
        self.top_bar_manager.remove_topbar_widget()
        self.top_bar_manager.remove_user_section()
        self.top_bar_manager.remove_project_section()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
