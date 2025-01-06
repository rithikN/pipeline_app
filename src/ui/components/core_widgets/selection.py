import logging
from typing import List
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal
from ui.components.forms.selection_form import Ui_SelectionForm
from ui.components.extensions.message_box import MessageBox

logger = logging.getLogger(__name__)


class SelectionWidget(QWidget):
    """
    A widget that provides combo boxes for selecting shots, episodes, scenes, tasks, and statuses.
    Emits a signal (selectionChanged) whenever the selection changes.
    """

    selectionChanged = Signal(dict)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        logger.debug("Initializing SelectionWidget.")

        # Instantiate the auto-generated UI form
        self._ui = Ui_SelectionForm()
        self._ui.setupUi(self)

        self.shot_comboBox = self._ui.shot_comboBox
        self.episode_comboBox = self._ui.episode_comboBox
        self.scene_comboBox = self._ui.scene_comboBox
        self.task_comboBox = self._ui.task_comboBox
        self.status_comboBox = self._ui.status_comboBox

        self._message_box = MessageBox()

        # Set up the UI and connections
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        logger.debug("Setting up UI for SelectionWidget.")
        self.setStyleSheet("""
            font-size: 12px; 
            font-weight: bold;  
        """)

    def _setup_connections(self):
        logger.debug("Setting up signal connections for SelectionWidget.")

        # For single-combo (shots), we connect currentTextChanged
        self.shot_comboBox.currentTextChanged.connect(self._emit_selection)

        # For multi-select combos (episodes/scenes/tasks/statuses),
        # assume they each have a selectionChanged signal
        self.episode_comboBox.selectionChanged.connect(self._emit_selection)
        self.scene_comboBox.selectionChanged.connect(self._emit_selection)
        self.task_comboBox.selectionChanged.connect(self._emit_selection)
        self.status_comboBox.selectionChanged.connect(self._emit_selection)

    def _emit_selection(self):
        logger.debug("Emitting selection from SelectionWidget.")
        selection = {
            "shot": self.shot_comboBox.currentText(),
            "episode": self.episode_comboBox.selectedItems(),
            "scene": self.scene_comboBox.selectedItems(),
            "task": self.task_comboBox.selectedItems(),
            "status": self.status_comboBox.selectedItems(),
        }
        self.selectionChanged.emit(selection)

    # --------------------------------------------------------------------
    #                  Helper Methods
    # --------------------------------------------------------------------

    def _set_single_selection(self, combo_box, new_value: str, label: str):
        """
        Helper method to set a single selected item in a combo box.
        """
        logger.debug(f"Setting current {label} to '{new_value}'.")
        current_text = combo_box.currentText()

        if new_value == current_text:
            logger.debug(f"{label.capitalize()} is already set; skipping.")
            return

        index = combo_box.findText(new_value)
        if index < 0:
            logger.debug(f"{label.capitalize()} '{new_value}' not found; skipping or handle as needed.")
            return

        combo_box.setCurrentIndex(index)
        logger.debug(f"{label.capitalize()} updated to '{new_value}'.")

    def _set_multiple_selections(self, combo_box, new_items: List[str], label: str):
        """
        Helper method to set multiple selected items in a combo box.
        """
        logger.debug(f"Setting current {label}: {new_items}")
        old_items = combo_box.selectedItems()

        if set(new_items) == set(old_items):
            logger.debug(f"{label.capitalize()} are already set; skipping.")
            return

        combo_box.setSelectedItems(new_items)
        logger.debug(f"{label.capitalize()} updated.")

    # --------------------------------------------------------------------
    #                  Public Setter Methods
    # --------------------------------------------------------------------

    def set_current_shot(self, shot: str):
        """
        Sets the shot in shot_comboBox only if it differs from
        the currently selected text. Blocks signals to prevent duplicates.
        """
        self._set_single_selection(self.shot_comboBox, shot, "shot")

    def set_current_episode(self, episodes: List[str]):
        """
        Sets the selected episodes in episode_comboBox if they're different
        from what's currently selected. Blocks signals to prevent duplicates.
        """
        self._set_multiple_selections(self.episode_comboBox, episodes, "episodes")

    def set_current_scene(self, scenes: List[str]):
        """
        Sets the selected scenes in scene_comboBox if they're different
        from what's currently selected. Blocks signals to prevent duplicates.
        """
        self._set_multiple_selections(self.scene_comboBox, scenes, "scenes")

    def set_current_task(self, tasks: List[str]):
        """
        Sets the selected tasks in task_comboBox if they're different
        from what's currently selected. Blocks signals to prevent duplicates.
        """
        self._set_multiple_selections(self.task_comboBox, tasks, "tasks")

    def set_current_status(self, statuses: List[str]):
        """
        Sets the selected statuses in status_comboBox if they're different
        from what's currently selected. Blocks signals to prevent duplicates.
        """
        self._set_multiple_selections(self.status_comboBox, statuses, "statuses")
