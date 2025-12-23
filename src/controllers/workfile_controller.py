# controllers/work_files_controller.py

import logging, platform
from pathlib import Path
import re
from datetime import datetime

from controllers.base_controller import BaseController
from services.data_service import create_file, version_up_file, check_ftp_connection
from pipeline.infra.rclone import copy_through_rclone
from services.constants import (
    CREATE_FILE_TASK_SLUG ,CREATE_FILE_USER_SLUG, CREATE_FILE_PLATFORM_KEY, CREATE_FILE_PLATFORM_HOME,
    TASK_SLUG, TASK_ASSIGNED, TASK_EMPLOYEE, TASK_EMPLOYEE_SLUG
)


logger = logging.getLogger(__name__)


class WorkFilesController(BaseController):
    """
    Orchestrates operations related to work files:
    - Create initial v000 file
    - Download file from server
    - Upload file to server (with version up)
    """

    # --------------------
    # Create v000 File
    # --------------------
    def handle_create_file(self, task_data: dict):
        """
        Handle creation of a new work file for a given task.

        Steps:
          1. Verify FTP connection.
          2. Call backend to create file record.
          3. Prepare folder structure and copy starter file locally.
          4. Emit fileCreated event via the event manager.

        Args:
            task_data (dict): Dictionary with task details.

        Returns:
            dict: Updated task data with work file info.

        Raises:
            RuntimeError: If FTP connection fails or backend call fails.
        """
        with self.operation(
                title="Create File",
                message=f"Creating V000 file for: {task_data.get('name')}",
                payload=task_data,
        ):
            # --------------------
            # 1. Connectivity check
            # --------------------
            if not check_ftp_connection(check_FTP_conn=True):
                raise RuntimeError("FTP connection failed")

            # --------------------
            # 2. Call backend
            # --------------------
            payload = {
                CREATE_FILE_TASK_SLUG: task_data[TASK_SLUG],
                CREATE_FILE_USER_SLUG: task_data[TASK_ASSIGNED][TASK_EMPLOYEE][TASK_EMPLOYEE_SLUG],
                CREATE_FILE_PLATFORM_KEY: platform.system().lower(),
                CREATE_FILE_PLATFORM_HOME: Path.home().as_posix(),
            }
            updated_task_data = create_file(payload)

            if not updated_task_data or updated_task_data.get("name") != task_data["name"]:
                raise RuntimeError("Failed to create work file record")

            # --------------------
            # 3. Prepare workspace
            # --------------------
            work_file = updated_task_data[WORK_FILES][0]
            self._create_empty_folder_structure(work_file) # ToDo
            self._copy_server_file_to_artist_local_drive(work_file) # ToDo

            # --------------------
            # 4. Emit event
            # --------------------
            event = Event(
                title="File Created",
                message=f"Created new work file {work_file.get('work_detail', {}).get('file_name')}",
                payload=work_file,
                type="success",
            )
            self.publish_event("fileCreated", event)

            return updated_task_data

    # --------------------
    # Download Work File
    # --------------------
    def handle_download_file(self, file_data: dict):
        with self.operation(
            title="Download File",
            message=f"Downloading {file_data['work_detail']['file_name']}",
            payload=file_data,
        ):
            if not check_ftp_connection(check_FTP_conn=True):
                raise RuntimeError("FTP connection failed")

            server_path = file_data["work_detail"].get("ftp_path")
            local_path = file_data["work_detail"].get("work_file")

            if not server_path or not local_path:
                raise RuntimeError("Invalid file paths for download")

            # Ensure local folder exists
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            status = copy_through_rclone("copyto", src=server_path, dest=local_path, flags=["--update"])
            if status != 0:
                raise RuntimeError(f"Failed to download {server_path}")

            return local_path

    # --------------------
    # Upload Work File + Version Up
    # --------------------
    def handle_upload_file(self, file_data: dict, task_data: dict):
        with self.operation(
            title="Upload File",
            message=f"Uploading {file_data['work_detail']['file_name']}",
            payload=file_data,
        ):
            if not check_ftp_connection(check_FTP_conn=True):
                raise RuntimeError("FTP connection failed")

            local_path = file_data["work_detail"].get("work_file")
            server_path = file_data["work_detail"].get("ftp_path")

            if not local_path or not server_path:
                raise RuntimeError("Invalid file paths for upload")

            status = copy_through_rclone("copyto", src=local_path, dest=server_path, flags=["--update"])
            if status != 0:
                raise RuntimeError(f"Failed to upload {local_path}")

            # Version up record in backend
            file_path = Path(local_path)
            last_saved = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%d-%m-%Y %I:%M %p")
            file_size = file_path.stat().st_size // (1024 * 1024)

            data_for_backend = {
                "artist_slug": task_data["artist_assigned"]["employee"]["slug"],
                "file_slug": file_data.get("slug"),
                "versions": [{
                    "version_up_file": file_path.as_posix(),
                    "last_saved_time": last_saved,
                    "file_size": file_size,
                }],
                "work_file_path": server_path,
                "file_sync_status": WFA,
            }

            updated_task_data = version_up_file(data_for_backend)
            if not updated_task_data:
                raise RuntimeError("Failed to sync version-up with backend")

            return updated_task_data
