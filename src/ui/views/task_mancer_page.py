"""
task_mancer_page.py
-------------------
UI Orchestration layer for the 3D Pipeline Task Manager.

Responsibilities:
- Manage Work and Review areas
- Wire up controllers and signals
- Delegate all heavy logic (publish, download, upload, etc.) to controllers
- React to structured events via SignalManager

All configurations (paths, Kitsu, rclone, etc.) are environment-driven through:
`pipeline/config/settings.py` (loads environment + dcc apps).
"""

import logging
from pathlib import Path
from copy import deepcopy

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import QTimer

# UI imports
from ui.components.forms.task_mancer_form import Ui_TaskMancer_Form
from ui.components.extensions.message_box import MessageBox
from ui.components.core_widgets.selection import SelectionWidget
from ui.components.core_widgets.task_list import TaskListWidget
from ui.components.core_widgets.work_files import WorkFilesWidget
from ui.components.core_widgets.applications import ApplicationsWidget
from ui.components.core_widgets.work_details import WorkDetailsWidget
from ui.components.core_widgets.task_details import TaskDetailsWidget
from ui.components.extensions.custom_tab import CustomTabWidget
from ui.components.extensions.progress_dialog import ProgressDialog

from ui.views.work_area_page import WorkAreaWidget
from ui.views.review_area_page import ReviewAreaWidget

from ui.utils.stylesheet_utils import load_stylesheet, setup_tab_styles
from services.data_service import (
    get_episodes, get_scenes, get_workFiles, get_workDetails,
    get_taskDetail, get_taskTypes, check_VPN_connection
)
from services.constants import PROJECT, PROJECT_NAME, PROJECT_SLUG, ARTIST_SLUG
from pipeline.events import Event
from pipeline.infra.threads.project_fetch_thread import ProjectDataFetchThread

# Config
from pipeline.config.settings import settings

logger = logging.getLogger(__name__)


class TaskMancerPage(QWidget):
    """
    Central UI component managing both Work and Review areas.

    Delegates:
      - Task operations → TaskController
      - File ops → WorkFilesController
      - File details / DCC monitoring → WorkDetailsController
      - Project-wide downloads → ProjectController
    """

    def __init__(
        self, prev_page_callback, signal_manager,
        task_controller, workfile_controller,
        work_details_controller, project_controller,
    ):
        super().__init__()
        logger.info("Initializing TaskMancerPage...")
        self.setObjectName("TaskMancerPage")

        # --- UI Setup ---
        self._ui = Ui_TaskMancer_Form()
        self._ui.setupUi(self)

        # Load stylesheet
        qss_path = Path.cwd() / "ui" / "stylesheets" / "task_mancer_page.qss"
        load_stylesheet(self, qss_path)

        # --- Core references ---
        self.prev_page_callback = prev_page_callback
        self.message_box = MessageBox()
        self.signal_manager = signal_manager

        # Controllers
        self.task_controller = task_controller
        self.workfile_controller = workfile_controller
        self.work_details_controller = work_details_controller
        self.project_controller = project_controller

        # --- Global progress dialog ---
        self.progress_dialog = ProgressDialog(self, title="Please wait", message="")
        self.progress_dialog.hide()

        # --- Subscriptions ---
        self._connect_signal_manager_events()

        # --- Data state ---
        self._project_data = None
        self._project = None
        self._taskStatus = None
        self._taskData = None
        self._task_list = None

        # UI state (used by _populate)
        self._search_text = ""
        self._selection_filters = {"shot": [], "episode": [], "scene": [], "task": [], "status": []}
        self._selected_task = ""
        self._selected_file = ""

        # Applications from config
        self.applications = settings.get("APPLICATIONS", [])

        # Tracking variables
        self.current_working_version = None
        self.last_sync_version_slug = None

        self.active_workers = []
        self._active_dialog = None
        self.exception_messages = []

        # Area setup placeholders
        self.areas = self._initialize_area_structure()

        # Sync flags
        self.sync_in_progress = False
        self.cancel_requested = False

        # Initialize tab widget
        self._setup_tab_widget()

    # ------------------------------------------------------------
    #  UI SETUP
    # ------------------------------------------------------------
    def _initialize_area_structure(self):
        """Initialize empty structure for both Work and Review areas."""
        return {
            "work": {
                "selection_widget": None,
                "task_list_widget": None,
                "file_widget": None,
                "applications_widget": None,
                "file_detail_widget": None,
                "area_widget": None,
                "search_text": "",
                "current_selection": {"shot": [], "episode": [], "scene": [], "task": [], "status": []},
            },
            "review": {
                "selection_widget": None,
                "task_list_widget": None,
                "task_detail_widget": None,
                "area_widget": None,
                "search_text": "",
                "current_selection": {"shot": [], "episode": [], "scene": [], "task": [], "status": []},
            },
        }

    def _setup_tab_widget(self):
        """Replace placeholder tab widget with a custom styled one."""
        logger.debug("Setting up CustomTabWidget for TaskMancerPage.")
        parent_layout = self._ui.TaskMancer_tabWidget.parentWidget().layout()
        if not parent_layout:
            raise RuntimeError("Parent layout for TaskMancer_tabWidget not found.")

        parent_layout.removeWidget(self._ui.TaskMancer_tabWidget)
        self._ui.TaskMancer_tabWidget.deleteLater()

        self._ui.TaskMancer_tabWidget = CustomTabWidget()
        parent_layout.addWidget(self._ui.TaskMancer_tabWidget)
        setup_tab_styles(self._ui.TaskMancer_tabWidget)

    def _connect_signal_manager_events(self):
        """Subscribe to structured cross-controller signals."""
        sm = self.signal_manager
        sm.progressStarted.connect(self._on_progress_started)
        sm.progressFinished.connect(self._on_progress_finished)
        sm.errorOccurred.connect(self._on_error)
        sm.fileCreated.connect(self._on_file_created)
        sm.assetListReady.connect(self._on_asset_list_ready)
        sm.assetTrackerError.connect(self._on_asset_tracker_error)
        sm.assetTrackerEmpty.connect(self._on_asset_tracker_empty)
        sm.download_triggered.connect(self._on_download_project_files)

    # ------------------------------------------------------------
    #  PROJECT LOADING
    # ------------------------------------------------------------
    def set_project(self, project_data, search_text="", selection_filters={},
                    selected_task="", selected_file=""):
        """Load and populate data for selected project."""
        logger.info(f"Setting project: {project_data[PROJECT][PROJECT_NAME]}")
        self._project = project_data[PROJECT]
        self._project_data = project_data

        # store UI state for population
        self._search_text = search_text or ""
        self._selection_filters = selection_filters or {"shot": [], "episode": [], "scene": [], "task": [], "status": []}
        self._selected_task = selected_task or ""
        self._selected_file = selected_file or ""

        if not check_VPN_connection():
            return None

        self._clear_ui()
        progress_dialog = ProgressDialog(self, title="Loading Project Data", message="Fetching data...")
        progress_dialog.show()

        self.data_thread = ProjectDataFetchThread(
            project_data = {
            "project_slug": project_data[PROJECT][PROJECT_SLUG],
            "artist_slug": project_data[ARTIST_SLUG],
        })

        # --- Callbacks ---
        def on_data_fetched(result):
            task_data, task_status = result
            self._task_list = task_data
            QTimer.singleShot(0, lambda: _build_and_populate_ui(task_data, task_status, progress_dialog))

        def _build_and_populate_ui(task_data, task_status, dialog_ref):
            if not task_data or not task_status:
                logger.error("Incomplete data received from the server.")
                self.message_box.show_error("Received incomplete data from the server.", "error", "On Refresh.")
                dialog_ref.close()
                return

            self._taskStatus = task_status
            self._taskData = task_data
            self._build_ui()
            self._populate(self._taskData, self._taskStatus)
            dialog_ref.close()

        def on_error(error_message):
            progress_dialog.close()
            logger.error(f"Error fetching data: {error_message}")
            self.message_box.show_error(f"Error: {error_message}")

        def on_cancel():
            self.cancel_requested = True
            logger.warning("Operation canceled by the user.")
            if self.data_thread.isRunning():
                self.data_thread.terminate()
            progress_dialog.close()

        # Connect signals
        self.data_thread.data_fetched.connect(on_data_fetched)
        self.data_thread.error_occurred.connect(on_error)
        progress_dialog.canceled.connect(on_cancel)

        # Start background fetch
        self.data_thread.start()
        progress_dialog.progress_bar.setRange(0, 0)

    # ------------------------------------------------------------
    #  UI BUILDING
    # ------------------------------------------------------------
    def _build_ui(self):
        logger.debug("Building TaskMancerPage UI components.")

        # Work Area
        work = self.areas["work"]
        work["selection_widget"] = SelectionWidget()
        work["task_list_widget"] = TaskListWidget()
        work["file_widget"] = WorkFilesWidget()
        work["file_detail_widget"] = WorkDetailsWidget(title="Work File Details")
        work["applications_widget"] = ApplicationsWidget(applications=self.applications)
        work["area_widget"] = WorkAreaWidget(
            work["selection_widget"], work["task_list_widget"],
            work["file_widget"], work["file_detail_widget"],
            work["applications_widget"]
        )

        # Review Area
        review = self.areas["review"]
        review["selection_widget"] = SelectionWidget()
        review["task_list_widget"] = TaskListWidget()
        review["task_detail_widget"] = TaskDetailsWidget("Task Details")
        review["area_widget"] = ReviewAreaWidget(review["task_list_widget"], review["task_detail_widget"])

        tab = self._ui.TaskMancer_tabWidget
        tab.clear()
        tab.addTab(work["area_widget"], "Work Area")
        tab.addTab(review["area_widget"], "Review")

        self._setup_connections()

    def _clear_ui(self):
        tab = self._ui.TaskMancer_tabWidget
        tab.clear()
        for area in self.areas.values():
            for key in list(area.keys()):
                if hasattr(area[key], "deleteLater"):
                    area[key] = None
                elif isinstance(area[key], dict) and key == "current_selection":
                    area[key] = {"shot": [], "episode": [], "scene": [], "task": [], "status": []}
                elif isinstance(area[key], str) and key == "search_text":
                    area[key] = ""

    # ------------------------------------------------------------
    #  POPULATION & FILTERS
    # ------------------------------------------------------------
    def _populate(self, task_data, task_status):
        """
        Populate both tabs with:
          - tasks + status colors
          - search text
          - selection combo contents
          - selected task & file
          - apply filters
        """
        logger.debug("Populating TaskMancerPage with fetched data.")
        if not task_data or not task_status:
            logger.warning("No task data or status data to populate.")
            return

        # 1) Set tasks + status colors on both lists
        for area_name in ("work", "review"):
            tlist = self.areas[area_name]["task_list_widget"]
            if tlist:
                tlist.set_tasks(task_data)
                tlist.set_task_status_colors(task_status)

        # 2) Apply search text to both lists
        for area_name in ("work", "review"):
            tlist = self.areas[area_name]["task_list_widget"]
            if tlist:
                tlist.search_lineEdit.setText(self._search_text)

        # 3) Populate selection widgets and set current values
        for area_name in ("work", "review"):
            sel = self.areas[area_name]["selection_widget"]
            if sel:
                self._populate_selection_widget(sel, self._selection_filters)

        # 4) If a task was specified, select it (mirror to both tabs)
        if self._selected_task:
            wlist = self.areas["work"]["task_list_widget"]
            rlist = self.areas["review"]["task_list_widget"]
            if rlist:
                rlist.set_selected_task(self._selected_task, emit_signal=True)
            elif wlist:
                wlist.set_selected_task(self._selected_task, emit_signal=True)

        # 5) If a file was specified, select it in WorkFiles
        if self._selected_file:
            wfwidget = self.areas["work"]["file_widget"]
            if wfwidget:
                wfwidget.set_selected_file(self._selected_file, emit_signal=True)

        # 6) Finally apply filters on both tabs
        self._apply_filters("work")
        self._apply_filters("review")

    def _populate_selection_widget(self, selection_widget, selection_filters=None):
        logger.debug("Populating selection widget with shot/episode/scene/task/status.")
        selection_filters = selection_filters or {}

        selection_widget.shot_comboBox.clear()
        selection_widget.shot_comboBox.addItems(["Shot", "Assets"])

        episodes = get_episodes(self._project, self._task_list)
        self._fill_combobox(selection_widget.episode_comboBox, "Select All", episodes)

        scenes = sorted(set(get_scenes(self._task_list)), reverse=True)
        self._fill_combobox(selection_widget.scene_comboBox, "Select All", list(scenes))

        task_types = sorted(set(get_taskTypes(self._task_list)))
        self._fill_combobox(selection_widget.task_comboBox, "Select All", task_types)

        selection_widget.status_comboBox.clear()
        selection_widget.status_comboBox.addItem("Select All")
        selection_widget.status_comboBox.addItems(self._taskStatus.keys())

        # ---- Apply saved filters (convert lists → single string) ----
        def _first_or_none(value):
            if isinstance(value, list):
                return value[0] if len(value) == 1 else None  # only apply if exactly one
            return value if isinstance(value, str) and value != "Select All" else None

        shot = _first_or_none(selection_filters.get("shot"))
        episode = _first_or_none(selection_filters.get("episode"))
        scene = _first_or_none(selection_filters.get("scene"))
        task = _first_or_none(selection_filters.get("task"))
        status = _first_or_none(selection_filters.get("status"))

        if shot:
            selection_widget.set_current_shot(shot)  # expects str
        if episode:
            selection_widget.set_current_episode(episode)  # expects str
        if scene:
            selection_widget.set_current_scene(scene)  # expects str
        if task:
            selection_widget.set_current_task(task)  # expects str
        if status:
            selection_widget.set_current_status(status)  # expects str

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
    #  CONTROLLER CONNECTIONS
    # ------------------------------------------------------------
    def _setup_connections(self):
        logger.debug("Connecting signals between widgets and controllers.")

        wsel = self.areas["work"]["selection_widget"]
        wlist = self.areas["work"]["task_list_widget"]
        wfwidget = self.areas["work"]["file_widget"]
        wfdwidget = self.areas["work"]["file_detail_widget"]

        # Selection syncing + search sync
        if wsel:
            wsel.selectionChanged.connect(lambda sel: self._on_selection_changed("work", sel))
            wsel.selectionChanged.connect(self._sync_selection)

        if wlist:
            wlist.search_lineEdit.textChanged.connect(lambda text: self._on_search_text_changed("work", text))
            wlist.taskSelected.connect(lambda task, data: self._populate_work_files(task, data))
            wlist.taskSelected.connect(self._sync_task_selection)
            wlist.search_lineEdit.textChanged.connect(self._sync_search_text)

            # Controller wires from TaskList
            wlist.downloadRequested.connect(self.task_controller.handle_download)
            wlist.uploadRequested.connect(self.task_controller.handle_upload)
            wlist.assetTrackerRequested.connect(self.task_controller.handle_asset_tracker)

        if wfwidget:
            wfwidget.fileSelected.connect(self._update_work_details)
            wfwidget.createRequested.connect(self._on_workfile_create_requested)
            wfwidget.downloadRequested.connect(self._on_download_requested)
            wfwidget.uploadRequested.connect(self._on_upload_requested)

        if wfdwidget:
            wfdwidget.launchRequested.connect(self._on_launch_requested)
            wfdwidget.explorerRequested.connect(self._on_explorer_requested)
            wfdwidget.publishRequested.connect(self._on_send_to_publish)

        # Review area sync
        rsel = self.areas["review"]["selection_widget"]
        rlist = self.areas["review"]["task_list_widget"]
        if rsel:
            rsel.selectionChanged.connect(lambda sel: self._on_selection_changed("review", sel))
            rsel.selectionChanged.connect(self._sync_selection)
        if rlist:
            rlist.search_lineEdit.textChanged.connect(lambda text: self._on_search_text_changed("review", text))
            rlist.taskSelected.connect(self._update_review_task_details)
            rlist.taskSelected.connect(self._sync_task_selection)
            rlist.search_lineEdit.textChanged.connect(self._sync_search_text)

    # ------------------------------------------------------------
    #  FILTER / SYNC HELPERS
    # ------------------------------------------------------------
    def _apply_filters(self, area):
        """Apply current search + selection filters to a task list."""
        tlist = self.areas[area]["task_list_widget"]
        if not tlist:
            return
        logger.debug(f"Applying filters for {area}")
        tlist.filter_tasks(
            search_text=self.areas[area]["search_text"],
            selection=self.areas[area]["current_selection"],
        )

    def _on_selection_changed(self, area, selection):
        logger.debug(f"{area.title()} selection changed: {selection}")
        self.areas[area]["current_selection"] = selection
        self._apply_filters(area)
        if area == "work":
            self._update_work_details({})
        else:
            self._update_review_task_details("")

    def _on_search_text_changed(self, area, text):
        logger.debug(f"{area.title()} search text changed: {text}")
        self.areas[area]["search_text"] = text
        self._apply_filters(area)
        if area == "work":
            self._update_work_details({})
        else:
            self._update_review_task_details("")

    def _sync_task_selection(self, task_name, *args):
        if self.sync_in_progress:
            return
        self.sync_in_progress = True
        try:
            sender = self.sender()
            wlist = self.areas["work"]["task_list_widget"]
            rlist = self.areas["review"]["task_list_widget"]
            if sender == wlist and rlist:
                rlist.set_selected_task(task_name, emit_signal=True)
            elif sender == rlist and wlist:
                wlist.set_selected_task(task_name, emit_signal=True)
        finally:
            self.sync_in_progress = False

    def _sync_selection(self, selection):
        if self.sync_in_progress:
            return
        self.sync_in_progress = True
        try:
            sender = self.sender()
            wsel = self.areas["work"]["selection_widget"]
            rsel = self.areas["review"]["selection_widget"]
            if sender == wsel and rsel:
                rsel.set_current_shot(selection.get("shot"))
                rsel.set_current_episode(selection.get("episode"))
                rsel.set_current_scene(selection.get("scene"))
                rsel.set_current_task(selection.get("task"))
                rsel.set_current_status(selection.get("status"))
            elif sender == rsel and wsel:
                wsel.set_current_shot(selection.get("shot"))
                wsel.set_current_episode(selection.get("episode"))
                wsel.set_current_scene(selection.get("scene"))
                wsel.set_current_task(selection.get("task"))
                wsel.set_current_status(selection.get("status"))
        finally:
            self.sync_in_progress = False

    def _sync_search_text(self, text):
        if self.sync_in_progress:
            return
        self.sync_in_progress = True
        try:
            sender = self.sender()
            wline = self.areas["work"]["task_list_widget"].search_lineEdit if self.areas["work"]["task_list_widget"] else None
            rline = self.areas["review"]["task_list_widget"].search_lineEdit if self.areas["review"]["task_list_widget"] else None
            if sender == wline and rline:
                rline.setText(text)
            elif sender == rline and wline:
                wline.setText(text)
        finally:
            self.sync_in_progress = False

    # ------------------------------------------------------------
    #  WORK/REVIEW DETAIL POPULATION
    # ------------------------------------------------------------
    def _populate_work_files(self, task_name, task_data):
        logger.debug(f"Updating WorkFilesWidget for task '{task_name}'.")
        wf = self.areas["work"]["file_widget"]
        if not wf:
            return
        files_data = get_workFiles(task_name, task_data)
        wf.set_task_data(task_data)
        wf.files = files_data

    def _update_work_details(self, workfile_data):
        logger.debug("Updating Work Area details.")
        fdw = self.areas["work"]["file_detail_widget"]
        if not workfile_data:
            if fdw:
                fdw.details_data = {}
            return

        self.current_working_version = workfile_data
        detail_data = get_workDetails(workfile_data)

        if fdw:
            fdw.details_data = detail_data
            try:
                preview_path, _ = self.work_details_controller.resolve_preview_file(workfile_data)
                fdw.set_preview(preview_path)
            except Exception:
                pass

    def _update_review_task_details(self, task_name):
        logger.debug(f"Updating Review details for task '{task_name}'.")
        tdw = self.areas["review"]["task_detail_widget"]
        if not tdw:
            return
        if not task_name:
            tdw.details_data = {}
            tdw.task_logs = []
            return
        task_detail_data = get_taskDetail(task_name, self._task_list)
        tdw.details_data = task_detail_data
        # demo logs (replace with real history when available)
        tdw.task_logs = [
            {
                "status": "IN_PROGRESS",
                "username": "abc",
                "date": "02-10 14:45",
                "comment": "Layout adjustments are currently in progress.",
                "task_status_color": "yellow",
            },
            {
                "status": "WAITING_APPROVAL",
                "username": "pqr",
                "date": "02-15 17:00",
                "comment": "Layout submitted for approval.",
                "task_status_color": "orange",
            },
        ]

    # ------------------------------------------------------------
    #  CONTROLLER DELEGATES
    # ------------------------------------------------------------
    def _on_workfile_create_requested(self, task_data: dict):
        self.workfile_controller.handle_create_file(task_data)

    def _on_download_requested(self, file_data: dict):
        self.workfile_controller.handle_download_file(file_data)

    def _on_upload_requested(self, file_data: dict):
        task_data = self.areas["work"]["file_widget"].task_data
        self.workfile_controller.handle_upload_file(file_data, task_data)

    def _on_send_to_publish(self):
        ctx = self._build_pipeline_context("PUBLISH")
        self.work_details_controller.send_to_publish(ctx)

    def _on_launch_requested(self, workfile_data: dict):
        self.work_details_controller.handle_launch(workfile_data)

    def _on_explorer_requested(self, workfile_data: dict):
        self.work_details_controller.handle_explorer(workfile_data)

    def _on_download_project_files(self):
        logger.debug("Triggered: Download Project Files")
        self.project_controller.handle_download_project_files(self._project_data)

    # ------------------------------------------------------------
    #  PIPELINE CONTEXT
    # ------------------------------------------------------------
    def _build_pipeline_context(self, process: str):
        wfwidget = self.areas["work"]["file_widget"]
        return {
            "page": self,
            "widgets": {
                "work_files": wfwidget,
                "work_details": self.areas["work"]["file_detail_widget"],
                "signal_manager": self.signal_manager,
            },
            "process": process,
            "process_title": "Publish File" if process == "PUBLISH" else "Send for Review",
            "working_version": deepcopy(self.current_working_version),
            "work_files_info": deepcopy(wfwidget.task_data.get("work_files")) if wfwidget and wfwidget.task_data else [],
            "artist_slug": deepcopy(wfwidget.task_data.get("artist_assigned", {}).get("employee", {}).get("slug")) if wfwidget and wfwidget.task_data else None,
            "task_name": deepcopy(wfwidget.task_data.get("name")) if wfwidget and wfwidget.task_data else None,
        }

    # ------------------------------------------------------------
    #  SIGNAL HANDLERS (from SignalManager)
    # ------------------------------------------------------------
    def _on_progress_started(self, event: Event):
        self.progress_dialog.setWindowTitle(event.title)
        self.progress_dialog.set_message(event.message)
        self.progress_dialog.progress_bar.setRange(0, 0)
        self.progress_dialog.show()

    def _on_progress_finished(self, event: Event):
        self.progress_dialog.close()
        self.message_box.show_message(event.message, "info", event.title)

    def _on_error(self, event: Event):
        self.progress_dialog.close()
        self.message_box.show_message(event.message, "error", event.title)

    def _on_file_created(self, event: Event):
        # Refresh the file list for the active task when a file is created
        wfwidget = self.areas["work"]["file_widget"]
        if wfwidget and wfwidget.task_data:
            wfwidget.files = wfwidget.task_data.get("work_files", [])

    def _on_asset_list_ready(self, event: Event):
        assets = event.payload.get("assets", [])
        task = event.payload.get("task", {})
        from ui.components.dialogs.asset_list_dialog import AssetListDialog
        dialog = AssetListDialog(task.get("name", "Unknown Task"), assets)
        dialog.exec()

    def _on_asset_tracker_error(self, event: Event):
        self.message_box.show_message(event.message, "error", event.title)

    def _on_asset_tracker_empty(self, event: Event):
        self.message_box.show_message(event.message, "warning", event.title)

    # ------------------------------------------------------------
    #  CLEANUP & NAV
    # ------------------------------------------------------------
    def closeEvent(self, event):
        if hasattr(self, "work_details_controller"):
            self.work_details_controller.shutdown_monitors()
        super().closeEvent(event)

    def _on_previous(self):
        logger.debug("Previous button clicked. Navigating back.")
        if self.prev_page_callback:
            self._clear_ui()
            self.prev_page_callback()

    def _refresh_task_manager_page(self):
        logger.debug("Refreshing the page")
        search_text = self.areas["work"]["search_text"]
        selection_filters = self.areas["work"]["current_selection"]
        try:
            selected_task = self.areas["work"]["file_widget"].task_data["name"]
            selected_file = ""
        except Exception:
            selected_task = ""
            selected_file = ""
        self.set_project(self._project_data, search_text, selection_filters, selected_task, selected_file)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    from ui.managers.signal_manager import SignalManager
    from controllers.task_controller import TaskController
    from controllers.workfile_controller import WorkFilesController
    from controllers.work_details_controller import WorkDetailsController
    from controllers.project_controller import ProjectController

    signal_manager = SignalManager()
    task_controller = TaskController(signal_manager)
    workfile_controller = WorkFilesController(signal_manager)
    work_details_controller = WorkDetailsController(signal_manager)
    project_controller = ProjectController(signal_manager)

    w = TaskMancerPage(None, signal_manager, task_controller, workfile_controller, work_details_controller, project_controller)
    w.show()
    sys.exit(app.exec())
