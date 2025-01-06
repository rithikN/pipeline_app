"""
task_mancer_page.py

Defines the TaskMancerPage, which manages the work and review areas
for tasks, files, scenes, and episodes in the 3D Pipeline.
"""

import logging

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QThread, Signal, QTimer

from ui.components.forms.task_mancer_form import Ui_TaskMancer_Form
from ui.components.extensions.message_box import MessageBox
from ui.components.core_widgets.selection import SelectionWidget
from ui.components.core_widgets.task_list import TaskListWidget
from ui.components.core_widgets.work_files import WorkFilesWidget
from ui.components.core_widgets.work_details import WorkDetailsWidget
from ui.components.core_widgets.file_details import FileDetailsWidget
from ui.components.core_widgets.task_details import TaskDetailsWidget
from ui.components.extensions.progress_dialog import ProgressDialog
from ui.components.extensions.custom_tab import CustomTabWidget

from ui.views.work_area_page import WorkAreaWidget
from ui.views.review_area_page import ReviewAreaWidget

from ui.utils.stylesheet_loader import load_stylesheet

from services.data_service import (
    get_episodes, get_scenes, get_tasks, get_workFiles, get_workDetails,
    get_fileDetails, get_taskDetail, get_taskLog, get_taskData, get_taskStatus
)

# Initialize logger
logger = logging.getLogger(__name__)


class TaskMancerPage(QWidget):
    """
    Manages the 'Work Area' and 'Review Area' in the 3D Pipeline, handling
    task, file, and scene selection and displaying relevant details.
    """

    def __init__(self, prev_page_callback):
        """
        Initialize the TaskMancerPage.

        Args:
            prev_page_callback (callable): Function to call when navigating back.
        """
        super().__init__()
        logger.info("Initializing TaskMancerPage...")
        self.setObjectName("TaskMancerPage")

        self._ui = Ui_TaskMancer_Form()
        self._ui.setupUi(self)

        # Load external stylesheet
        load_stylesheet(self, "ui/stylesheets/task_mancer_page.qss")

        # Callback and messaging
        self.prev_page_callback = prev_page_callback
        self.message_box = MessageBox()

        # Project and task status
        self._project = None
        self._taskStatus = None

        # -- To reduce repetition, store area-specific components in a dict --
        # This makes it easier to loop over areas for certain operations.
        self.areas = {
            "work": {
                "selection_widget": None,
                "task_list_widget": None,
                "file_widget": None,
                "file_detail_widget": None,
                "file_preview_widget": None,
                "area_widget": None,
                "search_text": "",
                "current_selection": {
                    "shot": [],
                    "episode": [],
                    "scene": [],
                    "task": [],
                    "status": []
                }
            },
            "review": {
                "selection_widget": None,
                "task_list_widget": None,
                "task_detail_widget": None,
                "area_widget": None,
                "search_text": "",
                "current_selection": {
                    "shot": [],
                    "episode": [],
                    "scene": [],
                    "task": [],
                    "status": []
                }
            }
        }

        # Synchronization flags
        self.sync_in_progress = False
        self.cancel_requested = False

        # Replace the default tab widget with a CustomTabWidget
        self._setup_tab_widget()

    # ------------------------------------------------------------
    #                  UI SETUP & TEARDOWN
    # ------------------------------------------------------------

    def _setup_tab_widget(self):
        """
        Replace the auto-generated tab widget with a CustomTabWidget
        for improved styling and control.
        """
        logger.debug("Setting up CustomTabWidget for TaskMancerPage.")
        if hasattr(self._ui, "TaskMancer_tabWidget"):
            parent_layout = self._ui.TaskMancer_tabWidget.parentWidget().layout()
            if not parent_layout:
                raise RuntimeError("Parent layout for TaskMancer_tabWidget not found.")

            # Remove the old tab widget
            parent_layout.removeWidget(self._ui.TaskMancer_tabWidget)
            self._ui.TaskMancer_tabWidget.deleteLater()

            # Create and add the new CustomTabWidget
            self._ui.TaskMancer_tabWidget = CustomTabWidget()
            parent_layout.addWidget(self._ui.TaskMancer_tabWidget)

            # Example style (could be loaded via stylesheet)
            self._ui.TaskMancer_tabWidget.setStyleSheet(
                """
                QTabBar::tab {
                    height: 30px;
                    width: 75px;
                    background: #010409;
                    color: #E1E1E8;
                    border: 0px solid #010409;
                    padding: 5px;
                    margin: 0px;
                }
                QTabBar::tab:selected {
                    background: #010409;
                    font-weight: bold;
                }
                QTabBar::tab:hover {
                    background: #010409;
                }
                QTabWidget::pane {
                    background: #010409;
                    border: 0px solid #444;
                    top: -1px;
                }
                """
            )
        else:
            raise RuntimeError("TaskMancer_tabWidget does not exist in the UI.")

    def _build_ui(self):
        """
        Build and initialize the dynamic UI components (selection widgets,
        task list widgets, file widgets, etc.) for both 'Work Area' and 'Review'.
        """
        logger.debug("Building UI components for TaskMancerPage.")

        # -- Create Work Area Widgets --
        self.areas["work"]["selection_widget"] = SelectionWidget()
        self.areas["work"]["task_list_widget"] = TaskListWidget()
        self.areas["work"]["file_widget"] = WorkFilesWidget()
        self.areas["work"]["file_detail_widget"] = WorkDetailsWidget(title="Work Files Details")
        self.areas["work"]["file_preview_widget"] = FileDetailsWidget(title="File Preview")

        # Container widget for Work Area
        self.areas["work"]["area_widget"] = WorkAreaWidget(
            self.areas["work"]["selection_widget"],
            self.areas["work"]["task_list_widget"],
            self.areas["work"]["file_widget"],
            self.areas["work"]["file_detail_widget"],
            self.areas["work"]["file_preview_widget"],
        )

        # -- Create Review Area Widgets --
        self.areas["review"]["selection_widget"] = SelectionWidget()
        self.areas["review"]["task_list_widget"] = TaskListWidget()
        self.areas["review"]["task_detail_widget"] = TaskDetailsWidget("Task Details")

        # Container widget for Review Area
        self.areas["review"]["area_widget"] = ReviewAreaWidget(
            self.areas["review"]["selection_widget"],
            self.areas["review"]["task_list_widget"],
            self.areas["review"]["task_detail_widget"],
        )

        # Clear and re-populate the tab widget
        self._ui.TaskMancer_tabWidget.clear()
        self._ui.TaskMancer_tabWidget.addTab(self.areas["work"]["area_widget"], "Work Area")
        self._ui.TaskMancer_tabWidget.addTab(self.areas["review"]["area_widget"], "Review")

        # Connect signals
        self._setup_connections()

    def _clear_ui(self):
        """
        Clear UI-related data and widgets so a fresh UI can be built later.
        """
        logger.debug("Clearing TaskMancerPage UI components.")
        self._ui.TaskMancer_tabWidget.clear()

        # Reset all references and states
        for area_name in self.areas:
            for key in self.areas[area_name]:
                if isinstance(self.areas[area_name][key], QWidget):
                    self.areas[area_name][key] = None
                elif isinstance(self.areas[area_name][key], dict):
                    # For 'current_selection', reset them
                    self.areas[area_name][key] = {
                        "shot": [],
                        "episode": [],
                        "scene": [],
                        "task": [],
                        "status": []
                    }
                elif isinstance(self.areas[area_name][key], str):
                    self.areas[area_name][key] = ""

        self.sync_in_progress = False

    # ------------------------------------------------------------
    #                 PROJECT & DATA FETCHING
    # ------------------------------------------------------------

    def set_project(self, project_name):
        """
        Set the current project, clear any existing UI, and fetch data from the server.

        Args:
            project_name (str): The name of the project.
        """
        logger.info(f"Setting project to '{project_name}' and fetching data.")
        self._project = project_name
        self._clear_ui()

        progress_dialog = ProgressDialog(
            self,
            title="Loading Project Data",
            message="Fetching data..."
        )
        progress_dialog.show()

        # Create and start a background thread to fetch data
        self.data_thread = DataFetchThread({"project_name": project_name})

        def on_data_fetched(task_data, task_status):
            """
            Handle successful data fetching from the server.
            """
            QTimer.singleShot(0, lambda: _build_and_populate_ui(task_data, task_status, progress_dialog))

        def _build_and_populate_ui(task_data, task_status, progress_dialog):
            """
            Build the UI and populate with data, then close the progress dialog once done.
            """
            if not task_data or not task_status:
                logger.error("Incomplete data received from the server.")
                self.message_box.show_error("Received incomplete data from the server.")
                progress_dialog.close()
                return

            self._taskStatus = task_status

            # 1. Build UI (this can be expensive if it involves many widgets/layouts)
            self._build_ui()

            # 2. Populate your UI with the fetched data
            self._populate(task_data, task_status)

            # 3. Now that all heavy UI work is done, close the progress dialog
            progress_dialog.close()

        def on_error(error_message):
            """
            Handle errors that occur during data fetching.
            """
            progress_dialog.close()
            logger.error(f"Error fetching data: {error_message}")
            self.message_box.show_error(f"Error: {error_message}")

        def on_cancel():
            """
            Handle user-cancelation of data fetching.
            """
            self.cancel_requested = True
            logger.warning("Operation canceled by the user.")
            if self.data_thread.isRunning():
                self.data_thread.terminate()
            progress_dialog.close()

        # Connect signals
        self.data_thread.data_fetched.connect(on_data_fetched)
        self.data_thread.error_occurred.connect(on_error)
        progress_dialog.canceled.connect(on_cancel)

        # Start thread & indefinite progress
        self.data_thread.start()
        progress_dialog.progress_bar.setRange(0, 0)

    # ------------------------------------------------------------
    #                 SHARED UI SIGNAL CONNECTIONS
    # ------------------------------------------------------------

    def _setup_connections(self):
        """
        Connect signals of widgets to their respective slots.
        """
        logger.debug("Setting up signal connections for TaskMancerPage.")

        # Work area signals
        work_selection = self.areas["work"]["selection_widget"]
        work_task_list = self.areas["work"]["task_list_widget"]
        work_file_widget = self.areas["work"]["file_widget"]

        if work_selection:
            work_selection.selectionChanged.connect(
                lambda sel: self._on_selection_changed("work", sel)
            )
            work_selection.selectionChanged.connect(self._sync_selection)

        if work_task_list:
            work_task_list.search_lineEdit.textChanged.connect(
                lambda text: self._on_search_text_changed("work", text)
            )
            work_task_list.taskSelected.connect(
                lambda task_name, data: self._populate_work_files(task_name, data)
            )
            work_task_list.taskSelected.connect(self._sync_task_selection)
            work_task_list.search_lineEdit.textChanged.connect(self._sync_search_text)

        if work_file_widget:
            work_file_widget.fileSelected.connect(self._update_work_details)

        # Review area signals
        review_selection = self.areas["review"]["selection_widget"]
        review_task_list = self.areas["review"]["task_list_widget"]

        if review_selection:
            review_selection.selectionChanged.connect(
                lambda sel: self._on_selection_changed("review", sel)
            )
            review_selection.selectionChanged.connect(self._sync_selection)

        if review_task_list:
            review_task_list.search_lineEdit.textChanged.connect(
                lambda text: self._on_search_text_changed("review", text)
            )
            review_task_list.taskSelected.connect(self._update_review_task_details)
            review_task_list.taskSelected.connect(self._sync_task_selection)
            review_task_list.search_lineEdit.textChanged.connect(self._sync_search_text)

    # ------------------------------------------------------------
    #                       POPULATION
    # ------------------------------------------------------------

    def _populate(self, task_data, task_status):
        """
        Populate the TaskMancerPage UI with data fetched from the server.

        Args:
            task_data (list): List of tasks or related info.
            task_status (dict): Status-color mapping or other status metadata.
        """
        logger.debug("Populating TaskMancerPage with fetched data.")
        if not task_data or not task_status:
            logger.warning("No task data or status data to populate.")
            return

        # Set tasks & status colors for both areas
        for area_name in ("work", "review"):
            task_list_widget = self.areas[area_name]["task_list_widget"]
            if task_list_widget:
                task_list_widget.set_tasks(task_data)
                task_list_widget.set_task_status_colors(task_status)

        # Populate selection widgets
        for area_name in ("work", "review"):
            selection_widget = self.areas[area_name]["selection_widget"]
            if selection_widget:
                self._populate_selection_widget(selection_widget)

    def _populate_selection_widget(self, selection_widget):
        """
        Populate shot, episode, scene, task, and status in the given selection widget.
        """
        logger.debug("Populating a selection widget with shots, episodes, scenes, tasks, status.")
        # Shots
        selection_widget.shot_comboBox.clear()
        selection_widget.shot_comboBox.addItems(["Shot", "Assets"])

        # Episodes
        episodes = get_episodes(self._project)
        self._fill_combobox(selection_widget.episode_comboBox, "Select All", episodes)

        # Scenes
        scenes = get_scenes(self._project)
        self._fill_combobox(selection_widget.scene_comboBox, "Select All", scenes)

        # Tasks
        tasks = get_tasks(self._project)
        self._fill_combobox(selection_widget.task_comboBox, "Select All", tasks)

        # Status
        selection_widget.status_comboBox.clear()
        selection_widget.status_comboBox.addItem("Select All")
        if self._taskStatus:
            selection_widget.status_comboBox.addItems(self._taskStatus.keys())

    @staticmethod
    def _fill_combobox(combobox, default_item, items):
        """
        Helper to fill a combobox with a default item plus a list of items.
        """
        combobox.clear()
        combobox.addItem(default_item)
        if items:
            combobox.addItems(items)

    # ------------------------------------------------------------
    #                WORK AREA LOGIC / SLOTS
    # ------------------------------------------------------------

    def _on_selection_changed(self, area, selection):
        """
        Called when the selection in either the Work or Review area changes.
        """
        logger.debug(f"{area.title()} selection changed: {selection}")
        self.areas[area]["current_selection"] = selection

        # Apply filters to the relevant task list
        self._apply_filters(area)
        # Clear out relevant details
        if area == "work":
            self._update_work_details({})
        else:
            self._update_review_task_details("")

    def _on_search_text_changed(self, area, text):
        """
        Called when the search text in either the Work or Review area changes.
        """
        logger.debug(f"{area.title()} search text changed: {text}")
        self.areas[area]["search_text"] = text
        self._apply_filters(area)

        # Clear details
        if area == "work":
            self._update_work_details({})
        else:
            self._update_review_task_details("")

    def _apply_filters(self, area):
        """
        Filter tasks in the specified area's task list based on current search text and selection.
        """
        task_list_widget = self.areas[area]["task_list_widget"]
        if not task_list_widget:
            return

        logger.debug(f"Applying {area} filters.")
        task_list_widget.filter_tasks(
            search_text=self.areas[area]["search_text"],
            selection=self.areas[area]["current_selection"]
        )

    def _populate_work_files(self, task_name, task_data):
        """
        Update the WorkFilesWidget with files related to the given task name.
        """
        logger.debug(f"Updating WorkFilesWidget for task '{task_name}'.")
        work_file_widget = self.areas["work"]["file_widget"]
        if not work_file_widget:
            return

        files_data = get_workFiles(task_data)
        work_file_widget.set_task_data(task_data)
        work_file_widget.files = files_data

    def _update_work_details(self, workfile_data):
        """
        Update details widgets for the selected work file in the Work Area.
        """
        logger.debug("Updating details for Work Area.")
        if not workfile_data:
            # Clear data if empty
            if self.areas["work"]["file_detail_widget"]:
                self.areas["work"]["file_detail_widget"].details_data = {}
            if self.areas["work"]["file_preview_widget"]:
                self.areas["work"]["file_preview_widget"].details_data = {}
            return

        detail_data = get_workDetails(workfile_data)
        preview_data = get_fileDetails(workfile_data)

        if self.areas["work"]["file_detail_widget"]:
            self.areas["work"]["file_detail_widget"].details_data = detail_data
        if self.areas["work"]["file_preview_widget"]:
            self.areas["work"]["file_preview_widget"].details_data = preview_data

    # ------------------------------------------------------------
    #                REVIEW AREA LOGIC / SLOTS
    # ------------------------------------------------------------

    def _update_review_task_details(self, task_name):
        """
        Update the task details and logs in the Review Area for the given task name.
        """
        logger.debug(f"Updating task details for Review Area, task '{task_name}'.")
        detail_widget = self.areas["review"]["task_detail_widget"]

        if not detail_widget:
            return

        # Clear if no task name
        if not task_name:
            detail_widget.details_data = {}
            detail_widget.task_logs = []
            return

        task_detail_data = get_taskDetail(task_name)
        task_log_data = get_taskLog(task_name)
        detail_widget.details_data = task_detail_data
        detail_widget.task_logs = task_log_data

    # ------------------------------------------------------------
    #                SYNCHRONIZATION LOGIC
    # ------------------------------------------------------------

    def _sync_task_selection(self, task_name, *args):
        """
        Synchronize task selection between work and review task lists.
        """
        if self.sync_in_progress:
            return

        self.sync_in_progress = True
        try:
            sender = self.sender()
            work_task_list = self.areas["work"]["task_list_widget"]
            review_task_list = self.areas["review"]["task_list_widget"]

            if sender == work_task_list:
                if review_task_list:
                    review_task_list.set_selected_task(task_name, emit_signal=True)
            elif sender == review_task_list:
                if work_task_list:
                    work_task_list.set_selected_task(task_name, emit_signal=True)
        finally:
            self.sync_in_progress = False

    def _sync_selection(self, selection):
        """
        Synchronize shot/episode/scene/task/status selection between work and review widgets.
        """
        if self.sync_in_progress:
            return

        self.sync_in_progress = True
        try:
            sender = self.sender()
            work_selection = self.areas["work"]["selection_widget"]
            review_selection = self.areas["review"]["selection_widget"]

            if sender == work_selection and review_selection:
                review_selection.set_current_shot(selection.get("shot"))
                review_selection.set_current_episode(selection.get("episode"))
                review_selection.set_current_scene(selection.get("scene"))
                review_selection.set_current_task(selection.get("task"))
                review_selection.set_current_status(selection.get("status"))
            elif sender == review_selection and work_selection:
                work_selection.set_current_shot(selection.get("shot"))
                work_selection.set_current_episode(selection.get("episode"))
                work_selection.set_current_scene(selection.get("scene"))
                work_selection.set_current_task(selection.get("task"))
                work_selection.set_current_status(selection.get("status"))
        finally:
            self.sync_in_progress = False

    def _sync_search_text(self, text):
        """
        Synchronize the search text between the work and review task lists.
        """
        if self.sync_in_progress:
            return

        self.sync_in_progress = True
        try:
            sender = self.sender()
            work_line_edit = None
            review_line_edit = None

            if self.areas["work"]["task_list_widget"]:
                work_line_edit = self.areas["work"]["task_list_widget"].search_lineEdit
            if self.areas["review"]["task_list_widget"]:
                review_line_edit = self.areas["review"]["task_list_widget"].search_lineEdit

            if sender == work_line_edit and review_line_edit:
                review_line_edit.setText(text)
            elif sender == review_line_edit and work_line_edit:
                work_line_edit.setText(text)
        finally:
            self.sync_in_progress = False

    # ------------------------------------------------------------
    #                  NAVIGATION & MISC
    # ------------------------------------------------------------

    def _on_previous(self):
        """
        Navigate back to the previous page, if a callback is provided.
        """
        logger.debug("Previous button clicked. Navigating back.")
        if self.prev_page_callback:
            self._clear_ui()
            self.prev_page_callback()

    def _download_project_files(self):
        """
        An example stub for further functionality.
        """
        logger.debug("Download project files menu action clicked.")


class DataFetchThread(QThread):
    """
    Thread responsible for fetching data related to tasks and their statuses.
    Emit signals on success or error.
    """
    data_fetched = Signal(list, dict)
    error_occurred = Signal(str)

    def __init__(self, project_data):
        """
        Initialize the DataFetchThread.

        Args:
            project_data (dict): Dictionary containing project-related information (e.g., project name).
        """
        super().__init__()
        self.project_data = project_data

    def run(self):
        """
        Fetch task data and task status in a background thread. Emit signals upon completion or error.
        """
        logger.debug("DataFetchThread started. Fetching task data and task status.")
        try:
            task_data = get_taskData(self.project_data)
            if not task_data:
                raise Exception("Failed to fetch task data.")
            task_status = get_taskStatus(self.project_data)
            if not task_status:
                raise Exception("Failed to fetch task status.")
            logger.debug("Data fetched successfully, emitting data_fetched signal.")
            self.data_fetched.emit(task_data, task_status)
        except Exception as e:
            logger.error(f"Error in DataFetchThread: {e}", exc_info=True)
            self.error_occurred.emit(str(e))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = TaskMancerPage(prev_page_callback=lambda: print("Back to previous page"))
    window.set_project("DemoProject")
    window.show()
    sys.exit(app.exec())
