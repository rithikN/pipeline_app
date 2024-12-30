# top_bar_manager.py

import logging
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMenuBar,
    QWidget,
    QHBoxLayout
)

from ui.components.core_widgets.menu_widget import CustomMenuWidget

# Import your constants
from services.constants import (
    APP_LABEL, UPDATE_LABEL, EXIT_LABEL,
    HELP_LABEL, ABOUT_LABEL, ABOUT_INFO_LABEL,
    EDIT_LABEL, LOGOUT_LABEL, WIKI_LABEL,
    DOWNLOAD_LABEL, EXIT_PROJECT_LABEL
)

logger = logging.getLogger(__name__)


class TopBarManager:
    """
    Handles creation and management of the application's top bar.
    """

    def __init__(self, menu_bar: QMenuBar, message_box, signal_manager):
        """
        Initialize the TopBarManager.

        Args:
            menu_bar (QMenuBar): The QMenuBar to which we'll add our actions.
            message_box (MessageBox): A custom MessageBox instance for dialogs.
            signal_manager (SignalManager): The SignalManager instance.
        """
        self.menu_bar = menu_bar
        self.message_box = message_box
        self.signal_manager = signal_manager

        # Keep references to dynamic sections and corner widget
        self.user_section_action = None
        self.project_section_action = None

        self.topbar_widget = None
        self.topbar_layout = None
        self.display_user_label = None
        self.display_project_label = None

        # Define base sections (always visible) with their actions
        self._base_sections = {
            APP_LABEL: [
                (UPDATE_LABEL, self._emit_update_triggered),
                (EXIT_LABEL, self._emit_exit_triggered),
            ],
            HELP_LABEL: [
                (WIKI_LABEL, self._emit_wiki_triggered),
                (ABOUT_LABEL, self._emit_about_triggered),
            ],
        }

        # Create base sections
        self._create_base_sections()
        self._apply_topbar_styles()

    # ----------------------------------------------------
    # Base Sections (loaded immediately in the constructor)
    # ----------------------------------------------------

    def _create_base_sections(self):
        """
        Iterate over self._base_sections and create each QMenu + actions.
        """
        logger.debug("Creating base sections.")
        for section_name, actions_data in self._base_sections.items():
            self._create_section(section_name, actions_data)

    def _create_section(self, section_name: str, actions_data: list[tuple[str, Callable]]):
        """
        Create a new QMenu in the menu bar with the given name,
        and add each action (label, callback) to it.
        """
        logger.debug(f"Creating section: {section_name}")
        new_menu = self.menu_bar.addMenu(section_name)
        for label, callback in actions_data:
            action = QAction(label, self.menu_bar)
            action.triggered.connect(callback)
            new_menu.addAction(action)
        # We don't store references to base sections because we never remove them.
        return new_menu

    def _apply_topbar_styles(self):
        """
        Apply custom styles to the QMenuBar and its items.
        """
        self.menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #000000;
                color: #E1E1E8;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                margin: 3px 10px;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #444; /* Highlight color when hovered */
            }
            QMenu {
                background-color: #333; /* Drop-down background */
                color: #E1E1E8;
            }
        """)

    # ---------------------
    # Emitters for Menu Actions
    # ---------------------

    def _emit_update_triggered(self):
        logger.debug("Update App action triggered.")
        self.signal_manager.update_triggered.emit()

    def _emit_exit_triggered(self):
        logger.debug("Exit action triggered.")
        self.signal_manager.exit_triggered.emit()

    def _emit_about_triggered(self):
        logger.debug("About action triggered.")
        self.signal_manager.about_triggered.emit()

    def _emit_wiki_triggered(self):
        logger.debug("App Wiki action triggered.")
        self.signal_manager.wiki_triggered.emit()

    def _emit_edit_triggered(self):
        logger.debug("Edit User Details action triggered.")
        self.signal_manager.edit_triggered.emit()

    def _emit_logout_triggered(self):
        logger.debug("Log Out action triggered.")
        self.signal_manager.logout_triggered.emit()

    def _emit_download_triggered(self):
        logger.debug("Download Project Files action triggered.")
        self.signal_manager.download_triggered.emit()

    def _emit_exit_project_triggered(self):
        logger.debug("Exit Project action triggered.")
        self.signal_manager.exit_project_triggered.emit()

    # -------------------------------------------------
    # Dynamic Sections (added/removed at runtime)
    # -------------------------------------------------

    def add_user_section(self):
        """
        Dynamically add a 'User' section with Edit / Log Out actions.
        We'll store the resulting QMenu's action (QAction) so we can remove it later.
        """
        logger.debug("Adding 'User' section.")
        if not self.user_section_action:
            # We can define user section actions here
            help_section_action = self.menu_bar.actions()[-1]
            user_actions = [
                (EDIT_LABEL, self._emit_edit_triggered),
                (LOGOUT_LABEL, self._emit_logout_triggered),
            ]
            # Create the QMenu
            user_menu = self._create_section("User", user_actions)
            # Insert it before the last menu (which is 'Help' in this example)
            self.user_section_action = self.menu_bar.insertMenu(help_section_action, user_menu)

    def remove_user_section(self):
        """
        Remove the 'User' section from the top bar, if it exists.
        """
        logger.debug("Removing 'User' section.")
        if self.user_section_action:
            self.menu_bar.removeAction(self.user_section_action)
            self.user_section_action = None

    def add_project_section(self):
        """
        Dynamically add a 'Project' section with Download / Exit Project actions.
        """
        logger.debug("Adding 'Project' section.")
        if not self.project_section_action:
            help_section_action = self.menu_bar.actions()[-1]
            project_actions = [
                (DOWNLOAD_LABEL, self._emit_download_triggered),
                (EXIT_PROJECT_LABEL, self._emit_exit_project_triggered),
            ]
            project_menu = self._create_section("Project", project_actions)
            self.project_section_action = self.menu_bar.insertMenu(help_section_action, project_menu)

    def remove_project_section(self):
        """
        Remove the 'Project' section from the top bar, if it exists.
        """
        logger.debug("Removing 'Project' section.")
        if self.project_section_action:
            self.menu_bar.removeAction(self.project_section_action)
            self.project_section_action = None

    # -------------------------------------------------
    # Top-Right Corner Widget
    # -------------------------------------------------

    def add_topbar_widget(self, parent, username=None, project_name=None):
        """
        Dynamically add a widget on the top-right corner to display
        username and/or project name.

        Args:
            parent (QWidget): The parent widget (usually MainWindow).
            username (str, optional): Current username to display.
            project_name (str, optional): Current project name to display.
        """
        logger.debug("Adding topbar widget to the QMenuBar.")
        self.topbar_widget = QWidget(parent)
        self.topbar_widget.setStyleSheet("background-color: transparent;")

        self.topbar_layout = QHBoxLayout(self.topbar_widget)
        self.topbar_layout.setContentsMargins(0, 0, 20, 0)
        self.topbar_layout.setSpacing(10)
        self.topbar_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Add project label if provided
        if project_name:
            self.display_project_label = CustomMenuWidget(project_name, parent=self.topbar_widget)
            self.display_project_label.setFixedSize(150, 30)
            self.topbar_layout.addWidget(self.display_project_label)

        # Add user label if provided
        if username:
            self.display_user_label = CustomMenuWidget(username, parent=self.topbar_widget)
            self.display_user_label.setFixedSize(150, 30)
            self.topbar_layout.addWidget(self.display_user_label)

        self.menu_bar.setCornerWidget(self.topbar_widget, Qt.Corner.TopRightCorner)
        self.topbar_widget.adjustSize()
        self.topbar_widget.show()
        self.menu_bar.update()

    def remove_topbar_widget(self):
        """
        Remove and delete the corner widget from the top bar.
        """
        logger.debug("Removing topbar widget from the QMenuBar.")
        if self.topbar_widget:
            self.menu_bar.setCornerWidget(None, Qt.Corner.TopRightCorner)
            self.topbar_widget.deleteLater()
            self.topbar_widget = None
            self.display_user_label = None
            self.display_project_label = None
            self.topbar_layout = None
