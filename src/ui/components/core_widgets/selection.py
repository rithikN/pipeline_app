"""
selection_widget.py

Defines the SelectionWidget, which provides combo boxes for selecting shots,
episodes, scenes, tasks, and statuses in the 3D Pipeline.
"""

import logging
from typing import List
from PySide6.QtWidgets import QWidget, QApplication
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
        """
        Initialize the SelectionWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
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
        """
        Configure additional UI elements if needed.
        Currently, it only uses the setupUi() from the generated form.
        """
        logger.debug("Setting up UI for SelectionWidget.")
        # Example: you can apply styles or additional properties here if needed.

    def _setup_connections(self):
        """
        Connect combo box signals to the internal _emit_selection slot.
        """
        logger.debug("Setting up signal connections for SelectionWidget.")

        self.shot_comboBox.currentTextChanged.connect(self._emit_selection)
        self.episode_comboBox.selectionChanged.connect(self._emit_selection)
        self.scene_comboBox.selectionChanged.connect(self._emit_selection)
        self.task_comboBox.selectionChanged.connect(self._emit_selection)
        self.status_comboBox.selectionChanged.connect(self._emit_selection)

    def _emit_selection(self):
        """
        Emit the selectionChanged signal with the current combo box selections.
        """
        logger.debug("Emitting selection from SelectionWidget.")
        selection = {
            "shot": self.shot_comboBox.currentText(),
            "episode": self.episode_comboBox.selectedItems(),
            "scene": self.scene_comboBox.selectedItems(),
            "task": self.task_comboBox.selectedItems(),
            "status": self.status_comboBox.selectedItems(),
        }
        self.selectionChanged.emit(selection)

    # -----------------------------
    # Public Methods for Updating UI
    # -----------------------------

    def set_current_shot(self, shot: str):
        """
        Set the current shot in the shot_comboBox.

        Args:
            shot (str): The shot to set.
        """
        logger.debug(f"Setting current shot to '{shot}'.")
        index = self.shot_comboBox.findText(shot)
        if index != -1:
            self.shot_comboBox.setCurrentIndex(index)

    def set_current_episode(self, episodes: List[str]):
        """
        Set the selected episodes in the episode_comboBox.

        Args:
            episodes (List[str]): A list of episode strings.
        """
        logger.debug(f"Setting current episodes: {episodes}")
        self.episode_comboBox.setSelectedItems(episodes)

    def set_current_scene(self, scenes: List[str]):
        """
        Set the selected scenes in the scene_comboBox.

        Args:
            scenes (List[str]): A list of scene strings.
        """
        logger.debug(f"Setting current scenes: {scenes}")
        self.scene_comboBox.setSelectedItems(scenes)

    def set_current_task(self, tasks: List[str]):
        """
        Set the selected tasks in the task_comboBox.

        Args:
            tasks (List[str]): A list of task strings.
        """
        logger.debug(f"Setting current tasks: {tasks}")
        self.task_comboBox.setSelectedItems(tasks)

    def set_current_status(self, statuses: List[str]):
        """
        Set the selected statuses in the status_comboBox.

        Args:
            statuses (List[str]): A list of status strings.
        """
        logger.debug(f"Setting current statuses: {statuses}")
        self.status_comboBox.setSelectedItems(statuses)


if __name__ == "__main__":
    import sys

    # Configure logging for standalone testing
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)

    widget = SelectionWidget()
    widget.show()

    sys.exit(app.exec())
