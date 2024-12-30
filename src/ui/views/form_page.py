"""
form_page.py

Defines the FormPage class for handling dynamic form input and navigation
within the 3D Pipeline application.
"""

import logging
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtGui import QMovie
from PySide6.QtCore import Qt, QSize

from ui.components.extensions.user_form.lineedit_component import LineEditComponent
from ui.components.extensions.user_form.combobox_component import ComboBoxComponent
from ui.components.forms.user_form import Ui_UserForm
from ui.utils.stylesheet_loader import load_stylesheet
from services.data_service import get_formUiData
from services.constants import TYPE, LABEL, ID, OPTIONS, FIELD_TYPE

# Initialize logger
logger = logging.getLogger(__name__)


class FormPage(QWidget):
    """
    Represents a form page where the user can fill out various fields
    (line edits, combo boxes) that are dynamically loaded from data service.
    """

    def __init__(self, next_page_callback=None, prev_page_callback=None):
        """
        Initialize the FormPage.

        Args:
            next_page_callback (callable):
                Function to call when proceeding to the next page (e.g., ProjectPage).
            prev_page_callback (callable):
                Function to call when navigating back to the previous page (e.g., LoginPage).
        """
        super().__init__()
        logger.info("Initializing FormPage...")

        # Callbacks
        self.next_page_callback = next_page_callback
        self.prev_page_callback = prev_page_callback

        # Track username
        self._username = None

        # Instantiate the auto-generated UI form
        self._ui = Ui_UserForm()
        self._ui.setupUi(self)

        # Load and apply the stylesheet
        load_stylesheet(self, "ui/stylesheets/form_style.css")

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """
        Configure UI elements and dynamically load form components.
        """
        logger.debug("Setting up UI for FormPage.")

        # Set up the GIF animation
        movie = QMovie("resources/logo.gif")
        self._ui.Welcome_label.setMovie(movie)
        movie.start()

        # Center the GIF label
        self._ui.Welcome_label.setAlignment(Qt.AlignCenter)

        # Retrieve form data
        self.form_ui_data = get_formUiData() or {}
        logger.debug(f"Loaded form UI data: {self.form_ui_data}")

        # Create a vertical layout for our scroll area contents
        self.scroll_layout = QVBoxLayout(self._ui.scrollAreaWidgetContents)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(0)

        # Dynamically add widgets based on form_ui_data
        for field in self.form_ui_data:
            field_type = field[TYPE]
            label = field[LABEL]
            field_id = field[ID]

            if field_type == FIELD_TYPE.lineedit.name:
                component = LineEditComponent(field_id, label)
                self.scroll_layout.addWidget(component)
            elif field_type == FIELD_TYPE.combobox.name:
                component = ComboBoxComponent(field_id, label, field[OPTIONS])
                self.scroll_layout.addWidget(component)
            else:
                logger.warning(f"Unknown field type encountered: {field_type}")

        # Add spacers between fields but not after the last field
        for i in range(self.scroll_layout.count() - 1):
            spacer_item = QSpacerItem(
                16, 13,
                QSizePolicy.Policy.Minimum,
                QSizePolicy.Policy.Fixed
            )

            self.scroll_layout.insertItem((i * 2) + 1, spacer_item)

    def _setup_connections(self):
        """
        Connect widgets to their respective event handlers.
        """
        logger.debug("Setting up connections for FormPage.")
        # "Next" button -> process and submit form data
        self._ui.next_button.clicked.connect(self._on_submit_form)

        # "Back" button -> invoke the previous page callback if available
        if self.prev_page_callback:
            self._ui.previous_button.clicked.connect(self.prev_page_callback)

    def set_username(self, username: str):
        """
        Set the username and update the displayed label.

        Args:
            username (str): The username to display.
        """
        self._username = username
        self._ui.user_label.setText(username)
        logger.debug(f"Username set to: {username}")

    def get_username(self) -> str:
        """
        Retrieve the stored username.

        Returns:
            str: Current username string.
        """
        return self._username

    def _on_submit_form(self):
        """
        Collect and process form data, then call the next page callback if available.
        """
        logger.debug("Submitting form data from FormPage.")
        form_data = {}
        form_data["username"] = self.get_username()

        # Gather input from the dynamic components
        for i in range(self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            if not item:
                continue
            widget = item.widget()
            if isinstance(widget, LineEditComponent):
                form_data[widget.id] = widget.get_value()
            elif isinstance(widget, ComboBoxComponent):
                form_data[widget.id] = widget.get_value()

        print(self._ui.horizontalSpacer_3.geometry())
        rect = self._ui.horizontalSpacer_3.geometry()
        width = rect.width()
        height = rect.height()
        print('form inside_verticalSpacer_5', self._ui.inside_verticalSpacer_5.geometry().width(),
              self._ui.inside_verticalSpacer_5.geometry().height())
        print('form inside_verticalSpacer_1', self._ui.inside_verticalSpacer_1.geometry().width(),
              self._ui.inside_verticalSpacer_1.geometry().height())
        print('form inside_verticalSpacer_3', self._ui.inside_verticalSpacer_3.geometry().width(),
              self._ui.inside_verticalSpacer_3.geometry().height())
        print('form inside_verticalSpacer_4', self._ui.inside_verticalSpacer_4.geometry().width(),
              self._ui.inside_verticalSpacer_4.geometry().height())
        print(f"Spacer1 width: {width}, height: {height}")

        print(self._ui.main_frame.height(), 111)
        if form_data:
            logger.info("Form data collected successfully.")
            logger.debug(f"Form data: {form_data}")
            if self.next_page_callback:
                self.next_page_callback(form_data)
        else:
            logger.warning("No form data was collected. Submission failed.")

    def resizeEvent(self, event):
        """
        Dynamically adjust the Welcome_label width on window resize.

        Args:
            event (QResizeEvent): The resize event object.
        """
        total_width = self.width()
        label_width = total_width // 2
        self._ui.Welcome_label.setFixedWidth(label_width)
        self._ui.Welcome_label.setMaximumSize(QSize(label_width, self.height()))
        super().resizeEvent(event)
