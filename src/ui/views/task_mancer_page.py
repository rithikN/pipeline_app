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

        # State variables
        self.current_search_text = ""
        self.current_selection = {
            "shot": [],
            "episode": [],
            "scene": [],
            "task": [],
            "status": []
        }
        self.sync_in_progress = False
        self.cancel_requested = False

        # Dynamically initialized UI components
        self.work_selection_widget = None
        self.work_tasklist_widget = None
        self.work_file_widget = None
        self.work_file_detail_widget = None
        self.file_preview_widget = None
        self.review_selection_widget = None
        self.review_tasklist_widget = None
        self.review_taskDetail_widget = None
        self.work_area_widget = None
        self.review_widget = None

        # Replace the default tab widget with a CustomTabWidget
        self._setup_tab_widget()

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

        # Create & style widgets for the Work Area
        self.work_selection_widget = SelectionWidget()
        self.work_tasklist_widget = TaskListWidget()
        self.work_file_widget = WorkFilesWidget()
        self.work_file_detail_widget = WorkDetailsWidget(title="Work Files Details")
        self.file_preview_widget = FileDetailsWidget(title="File Preview")

        # Create & style widgets for the Review Area
        self.review_selection_widget = SelectionWidget()
        self.review_tasklist_widget = TaskListWidget()
        self.review_taskDetail_widget = TaskDetailsWidget("Task Details")

        # Create container widgets (WorkAreaWidget, ReviewAreaWidget)
        self.work_area_widget = WorkAreaWidget(
            self.work_selection_widget,
            self.work_tasklist_widget,
            self.work_file_widget,
            self.work_file_detail_widget,
            self.file_preview_widget,
        )
        self.review_widget = ReviewAreaWidget(
            self.review_selection_widget,
            self.review_tasklist_widget,
            self.review_taskDetail_widget,
        )

        # Clear and re-populate the tab widget
        self._ui.TaskMancer_tabWidget.clear()
        self._ui.TaskMancer_tabWidget.addTab(self.work_area_widget, "Work Area")
        self._ui.TaskMancer_tabWidget.addTab(self.review_widget, "Review")

        # Finally, connect signals in the newly created widgets
        self._setup_connections()

    def _clear_ui(self):
        """
        Clear UI-related data and widgets so a fresh UI can be built later.
        """
        logger.debug("Clearing TaskMancerPage UI components.")
        self._ui.TaskMancer_tabWidget.clear()

        self.work_area_widget = None
        self.review_widget = None
        self.work_selection_widget = None
        self.work_tasklist_widget = None
        self.work_file_widget = None
        self.work_file_detail_widget = None
        self.file_preview_widget = None
        self.review_selection_widget = None
        self.review_tasklist_widget = None
        self.review_taskDetail_widget = None

        self.current_search_text = ""
        self.current_selection = {
            "shot": [],
            "episode": [],
            "scene": [],
            "task": [],
            "status": []
        }
        self.sync_in_progress = False

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
            # Don't close the dialog immediately; schedule the UI build with QTimer
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
        Navigate back to the previous page, if a callback is provided.
        """
        logger.debug("Download project files menu action clicked.")

    # ---------------------
    # SYNC & SELECTION LOGIC
    # ---------------------

    def sync_task_selection(self, task_name):
        """
        Synchronize task selection between work and review task lists.
        """
        if self.sync_in_progress:
            return

        self.sync_in_progress = True
        try:
            sender = self.sender()
            if sender == self.work_tasklist_widget:
                self.review_tasklist_widget.set_selected_task(task_name, emit_signal=True)
            elif sender == self.review_tasklist_widget:
                self.work_tasklist_widget.set_selected_task(task_name, emit_signal=True)
        finally:
            self.sync_in_progress = False

    def sync_selection(self, selection):
        """
        Synchronize shot/episode/scene/task/status selection between work and review widgets.
        """
        if self.sync_in_progress:
            return

        self.sync_in_progress = True
        try:
            sender = self.sender()
            if sender == self.work_selection_widget:
                self.review_selection_widget.set_current_shot(selection.get("shot"))
                self.review_selection_widget.set_current_episode(selection.get("episode"))
                self.review_selection_widget.set_current_scene(selection.get("scene"))
                self.review_selection_widget.set_current_task(selection.get("task"))
                self.review_selection_widget.set_current_status(selection.get("status"))
            elif sender == self.review_selection_widget:
                self.work_selection_widget.set_current_shot(selection.get("shot"))
                self.work_selection_widget.set_current_episode(selection.get("episode"))
                self.work_selection_widget.set_current_scene(selection.get("scene"))
                self.work_selection_widget.set_current_task(selection.get("task"))
                self.work_selection_widget.set_current_status(selection.get("status"))
        finally:
            self.sync_in_progress = False

    def sync_search_text(self, text):
        """
        Synchronize the search text between the work and review task lists.
        """
        if self.sync_in_progress:
            return

        self.sync_in_progress = True
        try:
            sender = self.sender()
            if sender == self.work_tasklist_widget.search_lineEdit:
                self.review_tasklist_widget.search_lineEdit.setText(text)
            elif sender == self.review_tasklist_widget.search_lineEdit:
                self.work_tasklist_widget.search_lineEdit.setText(text)
        finally:
            self.sync_in_progress = False

    # ---------------------
    # UI SIGNAL CONNECTIONS
    # ---------------------

    def _setup_connections(self):
        """
        Connect signals of widgets (selection, task list, file widgets) to their respective slots.
        """
        logger.debug("Setting up signal connections for TaskMancerPage.")

        # Work Area
        if self.work_selection_widget:
            self.work_selection_widget.selectionChanged.connect(self._on_work_selection_changed)
            self.work_selection_widget.selectionChanged.connect(self.sync_selection)

        if self.work_tasklist_widget:
            self.work_tasklist_widget.search_lineEdit.textChanged.connect(self._on_work_search_text_changed)
            self.work_tasklist_widget.taskSelected.connect(self._populate_work_files)
            self.work_tasklist_widget.taskSelected.connect(self.sync_task_selection)
            self.work_tasklist_widget.search_lineEdit.textChanged.connect(self.sync_search_text)

        if self.work_file_widget:
            self.work_file_widget.fileSelected.connect(self._update_details)

        # Review Area
        if self.review_selection_widget:
            self.review_selection_widget.selectionChanged.connect(self._on_review_selection_changed)
            self.review_selection_widget.selectionChanged.connect(self.sync_selection)

        if self.review_tasklist_widget:
            self.review_tasklist_widget.search_lineEdit.textChanged.connect(self._on_review_search_text_changed)
            self.review_tasklist_widget.taskSelected.connect(self._update_task_details)
            self.review_tasklist_widget.taskSelected.connect(self.sync_task_selection)
            self.review_tasklist_widget.search_lineEdit.textChanged.connect(self.sync_search_text)

    # ---------------------
    # DATA POPULATION
    # ---------------------

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

        # Populate 'Work' area widgets
        self.work_tasklist_widget.set_tasks(task_data)
        self.work_tasklist_widget.set_task_status_colors(task_status)

        # Populate 'Review' area widgets
        self.review_tasklist_widget.set_tasks(task_data)
        self.review_tasklist_widget.set_task_status_colors(task_status)

        # Populate selection widgets
        self._populate_selection_widgets([self.work_selection_widget, self.review_selection_widget])

    def _populate_selection_widgets(self, selection_widgets):
        """
        Populate shot, episode, scene, task, and status in each provided selection widget.

        Args:
            selection_widgets (list): A list of selection widgets (work/review).
        """
        logger.debug("Populating selection widgets (shots, episodes, scenes, tasks, status).")
        for widget in selection_widgets:
            if not widget:
                continue
            self._set_shots(widget)
            self._set_episodes(widget)
            self._set_scenes(widget)
            self._set_tasks(widget)
            self._set_status(widget)

    def _set_shots(self, selection_widget):
        selection_widget.shot_comboBox.clear()
        selection_widget.shot_comboBox.addItems(["Shot", "Assets"])

    def _set_episodes(self, selection_widget):
        episodes = get_episodes(self._project)
        selection_widget.episode_comboBox.clear()
        selection_widget.episode_comboBox.addItem("Select All")
        selection_widget.episode_comboBox.addItems(episodes)

    def _set_scenes(self, selection_widget):
        scenes = get_scenes(self._project)
        selection_widget.scene_comboBox.clear()
        selection_widget.scene_comboBox.addItem("Select All")
        selection_widget.scene_comboBox.addItems(scenes)

    def _set_tasks(self, selection_widget):
        tasks = get_tasks(self._project)
        selection_widget.task_comboBox.clear()
        selection_widget.task_comboBox.addItem("Select All")
        selection_widget.task_comboBox.addItems(tasks)

    def _set_status(self, selection_widget):
        selection_widget.status_comboBox.clear()
        selection_widget.status_comboBox.addItem("Select All")
        if self._taskStatus:
            selection_widget.status_comboBox.addItems(self._taskStatus.keys())

    # ---------------------
    # WORK AREA LOGIC
    # ---------------------

    def _on_work_selection_changed(self, selection):
        """
        Triggered when the selection in the Work Area changes.
        """
        logger.debug(f"Work selection changed: {selection}")
        self.current_selection = selection
        self._apply_work_filters()
        self._update_details({})  # Clear details when selection changes

    def _on_work_search_text_changed(self, text):
        """
        Triggered when the search text in the Work Area changes.
        """
        logger.debug(f"Work search text changed: {text}")
        self.current_search_text = text
        self._apply_work_filters()
        self._update_details({})  # Clear details when filtering

    def _apply_work_filters(self):
        """
        Filter tasks in the Work Area based on current search text and selection.
        """
        if self.work_tasklist_widget:
            logger.debug("Applying work filters.")
            self.work_tasklist_widget.filter_tasks(
                search_text=self.current_search_text,
                selection=self.current_selection
            )

    def _populate_work_files(self, task_name, task_data):
        """
        Update the WorkFilesWidget with files related to the given task name.
        """
        logger.debug(f"Updating WorkFilesWidget for task '{task_name}'.")
        if self.work_file_widget:
            files_data = get_workFiles(task_data)
            self.work_file_widget.files = files_data

    def _update_details(self, workfile_data):
        """
        Update details widgets for the selected work file.
        """
        logger.debug("Updating details for Work Area.")
        if self.work_file_detail_widget and workfile_data:
            print(workfile_data, '>>>>>>>>3455')
            detail_data = get_workDetails(workfile_data)

            self.work_file_detail_widget.details_data = detail_data

        if self.file_preview_widget and workfile_data:
            preview_data = get_fileDetails(workfile_data)
            self.file_preview_widget.details_data = preview_data

    # ---------------------
    # REVIEW AREA LOGIC
    # ---------------------

    def _on_review_selection_changed(self, selection):
        """
        Triggered when the selection in the Review Area changes.
        """
        logger.debug(f"Review selection changed: {selection}")
        self.current_selection = selection
        self._apply_review_filters()
        self._update_task_details("")  # Clear details when selection changes

    def _on_review_search_text_changed(self, text):
        """
        Triggered when the search text in the Review Area changes.
        """
        logger.debug(f"Review search text changed: {text}")
        self.current_search_text = text
        self._apply_review_filters()
        self._update_task_details("")  # Clear details when filtering

    def _apply_review_filters(self):
        """
        Filter tasks in the Review Area based on current search text and selection.
        """
        if self.review_tasklist_widget:
            logger.debug("Applying review filters.")
            self.review_tasklist_widget.filter_tasks(
                search_text=self.current_search_text,
                selection=self.current_selection,
            )

    def _update_task_details(self, task_name):
        """
        Update the task details and logs in the Review Area for the given task name.
        """
        logger.debug(f"Updating task details for Review Area, task '{task_name}'.")
        if self.review_taskDetail_widget and task_name:
            task_detail_data = get_taskDetail(task_name)
            self.review_taskDetail_widget.details_data = task_detail_data
            task_log_data = get_taskLog(task_name)
            self.review_taskDetail_widget.task_logs = task_log_data


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
            # task_status = get_taskStatus(self.project_data)
            task_status = {
                'In Progress': 'orange',
                'Approved': 'green'
            }
            if not task_status:
                raise Exception("Failed to fetch task status.")
            logger.debug("Data fetched successfully, emitting data_fetched signal.")
            self.data_fetched.emit(task_data, task_status)
        except Exception as e:
            logger.error(f"Error in DataFetchThread: {e}", exc_info=True)
            self.error_occurred.emit(str(e))


if __name__ == "__main__":
    # For testing purposes only:
    import sys

    app = QApplication(sys.argv)
    window = TaskMancerPage(prev_page_callback=lambda: print("Back to previous page"))
    window.set_project("DemoProject")
    window.show()
    sys.exit(app.exec())
