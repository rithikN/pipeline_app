"""
project_page.py

Defines the ProjectPage class, which displays a list of projects (as table cells/cards)
and allows the user to select and proceed to the next step in the 3D Pipeline.
"""

import logging
from PySide6.QtWidgets import (
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QHBoxLayout
)
from PySide6.QtCore import Qt, QSize

from ui.components.forms.project_form import Ui_ProjectForm
from ui.components.extensions.message_box import MessageBox
from ui.components.core_widgets.project_card import ProjectCard
from services.data_service import get_projects
from services.constants import PROJECT_NAME, PROJECT_TYPE, THUMBNAIL_PATH
from ui.utils.stylesheet_loader import load_stylesheet

# Initialize logger
logger = logging.getLogger(__name__)


class ProjectPage(QWidget):
    """
    Displays project cards in a grid and allows user selection and navigation.
    """

    def __init__(self, next_page_callback, prev_page_callback):
        """
        Initialize the ProjectPage.

        Args:
            next_page_callback (callable): Function to call when navigating to the next page.
            prev_page_callback (callable): Function to call when navigating back to the previous page.
        """
        super().__init__()
        logger.info("Initializing ProjectPage...")

        # UI setup
        self._ui = Ui_ProjectForm()
        self._ui.setupUi(self)
        load_stylesheet(self, r'ui/stylesheets/project_style.css')

        # Callbacks
        self.next_page_callback = next_page_callback
        self.prev_page_callback = prev_page_callback

        # Instance variables
        self.projects = []
        self.selected_row, self.selected_col = None, None

        # Constants for project card dimensions
        self.card_width, self.card_height, self.border_width = 250, 180, 30

        # Initialize components
        self.message_box = MessageBox()
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """
        Configure the UI components.
        """
        table = self._ui.project_tableWidget

        # Table settings
        table.setColumnCount(1)
        table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        table.setShowGrid(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setSelectionBehavior(QTableWidget.SelectItems)
        table.setFocusPolicy(Qt.StrongFocus)
        table.setIconSize(QSize(self.card_width, self.card_height))

        # Header visibility
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

        # Style settings
        table.setStyleSheet("""
            QTableWidget { background-color: #010409; }
            QTableWidget::item:selected { background-color: #3A4B6D; outline: none; }
            QTableWidget::item:hover { background-color: #3A4B60; outline: none; }
        """)

        # Disable the "Next" button initially
        self._ui.next_pushButton.setEnabled(False)

        # Attach a resize event handler
        table.resizeEvent = self._on_resize

    def _setup_connections(self):
        """
        Setup signal-slot connections.
        """
        logger.debug("Setting up connections for ProjectPage.")
        self._ui.next_pushButton.clicked.connect(self._on_next)
        self._ui.previous_pushButton.clicked.connect(self._on_previous)
        self._ui.project_tableWidget.cellClicked.connect(self._on_cell_clicked)
        self._ui.project_tableWidget.cellDoubleClicked.connect(self._on_cell_double_clicked)

    def set_form_data(self, form_data):
        """
        Set the form data and update the UI accordingly.

        Args:
            form_data (dict): Data from the FormPage.
        """
        logger.debug(f"Setting form data: {form_data}")
        self.projects = get_projects(form_data)
        self._populate_project_table()

    def _populate_project_table(self):
        """
        Populate the table widget with project cards.

        Args:
            projects (list): A list of project dictionaries.
        """
        if not self.projects:
            logger.warning("No projects to display.")
            return

        table = self._ui.project_tableWidget
        table_width = table.viewport().width()
        num_columns = max((table_width - self.border_width) // (self.card_width + self.border_width), 1)
        num_rows = -(-len(self.projects) // num_columns)  # Ceiling division

        table.setColumnCount(num_columns)
        table.setRowCount(num_rows)

        for col in range(num_columns):
            table.setColumnWidth(col, self.card_width + self.border_width)
        for row in range(num_rows):
            table.setRowHeight(row, self.card_height + self.border_width)

        for idx, project in enumerate(self.projects):
            row, col = divmod(idx, num_columns)
            project_card = ProjectCard(
                title=project.get(PROJECT_NAME, ""),
                project_type=project.get(PROJECT_TYPE, ""),
                parent=self,
                thumbnail=project.get(THUMBNAIL_PATH, "resources/empty_project.png")
            )
            container = self._wrap_project_card(project_card)
            table.setCellWidget(row, col, container)
            table.setItem(row, col, self._create_table_item(project))

        # Fill remaining cells
        self._fill_empty_cells(table, num_columns, len(self.projects))

    def _create_table_item(self, project):
        """
        Create a table item with project data.
        """
        item = QTableWidgetItem()
        item.setData(Qt.UserRole, project)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        return item

    def _wrap_project_card(self, project_card):
        """
        Wrap a project card in a transparent container.
        """
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(project_card)
        return container

    def _fill_empty_cells(self, table, num_columns, num_projects):
        """
        Disable selection and hover for empty cells.
        """
        for idx in range(num_projects, table.rowCount() * num_columns):
            row, col = divmod(idx, num_columns)
            item = QTableWidgetItem()
            item.setFlags(Qt.NoItemFlags)
            table.setItem(row, col, item)

    def _on_previous(self):
        """
        Navigate to the previous page.
        """
        if self.prev_page_callback:
            self.prev_page_callback()

    def _on_next(self):
        """
        Navigate to the next page with the selected project data.
        """
        table = self._ui.project_tableWidget
        item = table.item(self.selected_row, self.selected_col)
        if item and (project_data := item.data(Qt.UserRole)):
            self.next_page_callback(project_data)

    def _on_cell_clicked(self, row, col):
        """
        Handle cell click event.
        """
        table = self._ui.project_tableWidget
        item = table.item(row, col)
        if item and item.data(Qt.UserRole):
            self.selected_row, self.selected_col = row, col
            self._ui.next_pushButton.setEnabled(True)

    def _on_cell_double_clicked(self, row, col):
        """
        Handle cell double-click event.
        """
        table = self._ui.project_tableWidget
        item = table.item(row, col)
        if item and (project_data := item.data(Qt.UserRole)):
            self.next_page_callback(project_data)

    def _on_resize(self, event):
        """
        Handle table resize event.
        """
        if self.projects:
            self._populate_project_table()
