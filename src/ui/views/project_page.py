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

# Initialize logger
logger = logging.getLogger(__name__)


class ProjectPage(QWidget):
    """
    The ProjectPage displays project cards in a grid (QTableWidget).
    Allows selection and navigation to the next page.
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

        # UI data & callbacks
        self._ui = Ui_ProjectForm()
        self._ui.setupUi(self)

        self.message_box = MessageBox()
        self.next_page_callback = next_page_callback
        self.prev_page_callback = prev_page_callback
        self.form_data = {}
        self.projects = []

        # ProjectCard dimensions
        self.card_width = 250
        self.card_height = 180
        self.border_width = 30

        # Keep track of user selection
        self.selected_row = None
        self.selected_col = None

        # Perform setup
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """
        Configure UI elements (table widget, styles, etc.) for the ProjectPage.
        """
        logger.debug("Setting up UI for ProjectPage.")
        table = self._ui.project_tableWidget
        bottom_frame = self._ui.bottom_frame
        next_btn = self._ui.next_pushButton

        # Configure QTableWidget
        table.setColumnCount(1)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        table.setShowGrid(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setFocusPolicy(Qt.StrongFocus)
        table.verticalHeader().setVisible(False)
        table.setSelectionMode(QTableWidget.SingleSelection)
        table.setSelectionBehavior(QTableWidget.SelectItems)
        table.setIconSize(QSize(self.card_width, self.card_height))

        table.setStyleSheet("""
            QTableWidget {
                background-color: #010409;
            }
            QTableWidget::item:selected {
                background-color: #3A4B6D;
                border: 1px solid #005bb5;
            }
            QTableWidget::item:hover {
                background-color: #3A4B60;
            }
        """)

        bottom_frame.setStyleSheet("background-color: #010409;")

        # Disable "Next" button initially
        next_btn.setEnabled(False)

        # Recalculate layout on resize
        # We override the table's resizeEvent with our own method
        table.resizeEvent = self._on_resize

    def _setup_connections(self):
        """
        Connect signals to their corresponding slots.
        """
        logger.debug("Setting up connections for ProjectPage.")
        self._ui.next_pushButton.clicked.connect(self._on_next)
        self._ui.previous_pushButton.clicked.connect(self._on_previous)
        self._ui.project_tableWidget.cellClicked.connect(self._on_cell_clicked)
        self._ui.project_tableWidget.cellDoubleClicked.connect(self._on_cell_double_clicked)

    def _on_previous(self):
        """
        Handle the 'Previous' button click event.
        """
        logger.debug("Previous button clicked. Navigating back.")
        if self.prev_page_callback:
            self.prev_page_callback()

    def set_form_data(self, form_data):
        """
        Set the form data and update the UI accordingly.

        Args:
            form_data (dict): Data from the FormPage.
        """
        logger.debug(f"Setting form data on ProjectPage: {form_data}")
        self.form_data = form_data

        # Load projects using the data service
        self.projects = self._load_projects()
        logger.debug(f"Loaded projects: {self.projects}")

        # Populate the table with project cards
        self._populate_project_table(self.projects)

    def _populate_project_table(self, projects):
        """
        Populate the table widget with project cards.

        Args:
            projects (list): A list of project dictionaries.
        """
        logger.debug("Populating project table...")
        if not projects:
            logger.warning("No projects available to populate.")
            return

        table = self._ui.project_tableWidget
        table_width = table.viewport().width()

        # Calculate how many columns can fit
        num_columns = self._calculate_columns(table_width)
        num_rows = (len(projects) + num_columns - 1) // num_columns

        table.setColumnCount(num_columns)
        table.setRowCount(num_rows)

        for col in range(num_columns):
            table.setColumnWidth(col, self.card_width + self.border_width)
        for row in range(num_rows):
            table.setRowHeight(row, self.card_height + self.border_width)

        row, col = 0, 0
        for project in projects:
            project_name = project.get(PROJECT_NAME, "").strip()
            project_type = project.get(PROJECT_TYPE, "").strip()
            thumbnail_path = project.get(THUMBNAIL_PATH, "resources/empty_project.png").strip()

            item = QTableWidgetItem("")
            if project_name and project_type:
                item.setData(Qt.UserRole, project)
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

                project_card = ProjectCard(
                    title=project_name,
                    project_type=project_type,
                    parent=self,
                    thumbnail=thumbnail_path
                )

                # Create a container to center the ProjectCard
                container = QWidget()
                container.setStyleSheet("background: transparent;")
                container.setAttribute(Qt.WA_TransparentForMouseEvents, True)

                layout = QHBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                layout.setAlignment(Qt.AlignCenter)
                layout.addWidget(project_card)

                table.setCellWidget(row, col, container)
            else:
                # If project_name and project_type are empty, disable selection
                item.setFlags(Qt.NoItemFlags)

            table.setItem(row, col, item)

            col += 1
            if col >= num_columns:
                col = 0
                row += 1

        table.setStyleSheet("""
            QTableWidget {
                background-color: #010409;
            }
            QTableWidget::item:selected {
                background-color: #3A4B6D;
                border: 1px solid #005bb5;
            }
            QTableWidget::item:hover:!enabled {
                background-color: transparent;
            }
        """)

    def _calculate_columns(self, table_width):
        """
        Calculate how many columns can fit based on the table width.

        Args:
            table_width (int): The width of the table's viewport.

        Returns:
            int: Number of columns that can fit.
        """
        available_width = table_width - self.border_width
        columns = max(available_width // (self.card_width + self.border_width), 1)
        logger.debug(f"Calculated {columns} columns for width {table_width}.")
        return columns

    def _on_resize(self, event):
        """
        Handle resizing of the table widget.
        """
        logger.debug("ProjectPage table resized. Recalculating layout.")
        if self.projects:
            self._populate_project_table(self.projects)

    def _on_cell_clicked(self, row, col):
        """
        Handle single cell click (selection).
        """
        logger.debug(f"Cell clicked at row={row}, col={col}.")
        table = self._ui.project_tableWidget
        table.clearSelection()

        item = table.item(row, col)
        if not item or not table.cellWidget(row, col):
            logger.debug("Clicked cell is empty or does not contain a project.")
            return

        # Mark as selected and enable the "Next" button
        item.setSelected(True)
        self.selected_row = row
        self.selected_col = col
        self._ui.next_pushButton.setEnabled(True)

    def _on_cell_double_clicked(self, row, col):
        """
        Handle double-click on a project cell (shortcut to 'Next').
        """
        logger.debug(f"Cell double-clicked at row={row}, col={col}.")
        table = self._ui.project_tableWidget
        item = table.item(row, col)
        if item and item.data(Qt.UserRole) == "empty":
            logger.debug("Double-clicked cell is empty; ignoring.")
            return

        project_data = item.data(Qt.UserRole)
        if not project_data.get(PROJECT_NAME):
            logger.debug(f"No {PROJECT_NAME} key found in {project_data}.")
            return

        project_name = project_data[PROJECT_NAME]
        logger.info(f"Double-clicked project: {project_name}")
        self.next_page_callback(project_data)

    def _on_next(self):
        """
        Handle the "Next" button click. Pass the selected project to the callback.
        """
        logger.debug("Next button clicked.")
        if self.selected_col is None or self.selected_row is None:
            logger.debug("No cell is selected; ignoring 'Next' click.")
            return

        table = self._ui.project_tableWidget
        item = table.item(row, col)
        if item and item.data(Qt.UserRole) == "empty":
            logger.debug("Double-clicked cell is empty; ignoring.")
            return

        project_data = item.data(Qt.UserRole)
        if not project_data.get(PROJECT_NAME):
            logger.debug(f"No {PROJECT_NAME} key found in {project_data}.")
            return

        project_name = project_data[PROJECT_NAME]
        logger.info(f"Double-clicked project: {project_name}")
        self.next_page_callback(project_data)

    def _load_projects(self):
        """
        Load projects based on the current form_data.

        Returns:
            list: A list of project dictionaries.
        """
        logger.debug("Loading projects from data service.")
        return get_projects(self.form_data)
