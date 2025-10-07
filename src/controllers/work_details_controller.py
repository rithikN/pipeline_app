import logging
import os, subprocess
from pathlib import Path

from controllers.base_controller import BaseController
from services.data_service import publish_file

from pipeline.steps.connection import ValidationConnectionStep
from pipeline.steps.validate import ValidateFilesStep, ValidateFoldersStep
from pipeline.steps.media_info import ValidateMediaInfo
from pipeline.steps.copy import (
    CopyLocalOutFileStep,
    CopyWorkFileStep,
    CopyPreviewFileStep,
    CopyPublishFilesStep,
)
from pipeline.steps.kitsu import ValidateTaskStatusStep, UpdateKitsuStep
from pipeline.steps.publish import PublishFileStep
from pipeline.steps.success_message import SuccessMessageStep
from services.constants import PUB
from pipeline.manager import PipelineManager
from ui.managers.signal_manager import SignalManager

from pipeline.utils.preview_utils import verify_and_return_preview_file

logger = logging.getLogger(__name__)

class WorkDetailsController(BaseController):
    """
    Handles operations from WorkDetailsWidget:
    - Launch file in DCC app
    - Open in explorer
    - Publish file
    - Handle version-up events
    """

    def __init__(self, event_manager=None):
        super().__init__(event_manager=event_manager)
        # Keep track of active FileThreadLauncher monitors
        self.monitors: dict[str, FileThreadLauncher] = {}

    def handle_launch(self, details: dict):
        """
        Launch a DCC application and monitor the file using a dedicated thread.
        Emits structured events instead of UI message boxes.
        """
        with self.operation(
            title=" Launch File",
            message=f"Opening file {details.get('work_detail', {}).get('file_name')}",
            payload=details,
        ):
            app_executable_path = resolve_executable(details)
            local_work_file = resolve_work_file(details)


            if not app_executable_path or not local_work_file:
                self.publish_event(
                    "errorOccurred",
                    Event(type="error", title="Launch Error", message="Missing required data for launching.")
                )
                return

            if local_work_file in self.monitors:
                self.publish_event(
                    "errorOccurred",
                    Event(type="warning", title="File Open", message=f"File {local_work_file} is already open.")
                )
                return

            monitor = FileThreadLauncher(app_executable_path, local_work_file)
            self.monitors[local_work_file] = monitor

            # ToDo NOTE:
            # For now, FileThreadLauncher signal wiring is inside the controller for backward compatibility.
            # In future (see Roadmap Phase 2.1 – Pipeline Step Decoupling),
            # move this into infra/dcc_monitor.py so the controller just orchestrates
            # and publishes structured events via event_manager.

            # Wire signals back into event_manager so UI/CLI can respond
            monitor.file_opened.connect(lambda msg: self.publish_event(
                "progressStarted", Event(
                    type="info", title="File Opened",
                    message=msg, payload={"file": local_work_file}
                )
            ))
            monitor.file_closed.connect(lambda msg: self._on_file_closed(msg, local_work_file))
            monitor.file_versioned_up.connect(lambda data: self._on_file_versioned_up(data))
            monitor.error.connect(lambda msg: self.publish_event(
                "errorOccurred", Event(
                    type="error", title="Monitor Error",
                    message=msg, payload={"file": local_work_file}
                )
            ))

            monitor.start()

    def handle_explorer(self, details_data: dict):
        with self.operation(
                title="Open Explorer",
                message=f"Explorer for {details_data.get('work_detail', {}).get('file_name')}",
                payload=details_data,
        ):
            work_detail = details_data.get("work_detail", {})
            file_path = work_detail.get("work_file")

            if not file_path:
                raise RuntimeError("No file path found")

            parent_dir = Path(file_path).parent

            try:
                if os.name == "nt":  # Windows
                    os.startfile(parent_dir.as_posix())
                else:  # macOS/Linux
                    subprocess.run(["open", parent_dir.as_posix()], check=True)
            except Exception as e:
                raise RuntimeError(f"Failed to open explorer for {file_path}: {e}") from e

            return parent_dir

    def send_to_publish(self, ctx: dict):
        """
        Run the publish pipeline for the provided context.
        """
        with self.operation(
                title="Publish File",
                message=f"Publishing file {ctx.get('working_version', {}).get('work_detail', {}).get('file_name')}",
                payload=ctx,
        ):
            signal_manager = ctx.get('widgets', {}).get('signal_manager')
            steps = [
                ValidationConnectionStep(),
                ValidateTaskStatusStep(),
                ValidateFoldersStep(),
                ValidateFilesStep(),
                ValidateMediaInfo(),
                CopyLocalOutFileStep(),
                CopyWorkFileStep(),
                CopyPreviewFileStep(),
                CopyPublishFilesStep(),
                UpdateKitsuStep(status=PUB),
                PublishFileStep(),
                SuccessMessageStep(signal_manager=signal_manager, refresh_app=True),
            ]

            PipelineManager(steps).run(ctx)
            return ctx

    def handle_version_up(self, current_working_version: dict, task_data: dict, version_data: dict):
        with self.operation(
            title="Version Up",
            message=f"Processing version up for {version_data.get('new_file')}",
            payload=version_data,
        ):
            new_version_entry = deepcopy(current_working_version)
            old_file = version_data.get("recent_file")
            new_file = version_data.get("new_file")
            new_version_path = Path(os.path.dirname(old_file)) / new_file

            if not new_file:
                logger.debug("No new version file detected.")
                return None

            # Build new version entry
            file_name = os.path.basename(new_file)
            match = re.search(r'_v(\d+)', file_name)
            if match:
                version_number = int(match.group(1))
                new_version_entry["version"] = f"{version_number:03}"

            new_version_entry["file_size"] = version_data.get("new_file_size")
            new_version_entry["status"] = "in_progress"
            new_version_entry["date"] = version_data.get("new_file_last_saved_date")
            new_version_entry["slug"] = None
            new_version_entry["work_detail"]["filename"] = file_name
            new_version_entry["work_detail"]["last_saved"] = version_data.get("new_file_last_saved_time")
            new_version_entry["work_detail"]["locked_status"] = "Unlocked"
            new_version_entry["work_detail"]["work_file"] = new_version_path.as_posix()
            new_version_entry["work_detail"]["preview_path"] = "N/A"
            new_version_entry["work_detail"]["local_preview_path"] = ""
            new_version_entry["preview_detail"]["preview_path"] = ""
            new_version_entry["preview_detail"]["local_preview_path"] = ""

            # Update task_data
            task_data["work_files"].append(new_version_entry)

            # Emit event so UI/CLI can refresh
            event = Event(
                type="success",
                title="Version Up",
                message=f"New version {file_name} created",
                payload={"task_data": task_data, "new_version": new_version_entry},
            )
            self.publish_event("fileVersioned", event)

            return new_version_entry

    def shutdown_monitors(self):
        """
        Stop all running monitors and clear the registry.
        """
        for monitor in list(self.monitors.values()):
            try:
                monitor.stop()
            except Exception as e:
                self.logger.warning(f"Error stopping monitor {monitor}: {e}")
        self.monitors.clear()
        self.logger.info("All monitors stopped and cleared.")

    def resolve_preview_file(self, details_data: dict):
        """
        Resolve the best preview file for the given work details.
        """
        work_detail = details_data.get("work_detail", {})
        work_file = work_detail.get("file_name")
        work_task_name = Path(work_file).stem if work_file else None

        if not work_task_name:
            return None, None

        return verify_and_return_preview_file(details_data, work_task_name)



