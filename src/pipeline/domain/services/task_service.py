"""
pipeline/domain/services/task_service.py

Provides services for task operations such as downloading folders and dependencies.
"""

import os
import logging
from pathlib import Path

from pipeline.infra.rclone import copy_through_rclone
from pipeline.infra.paths import convert_path_for_current_os
from pipeline.domain.task_folders import TASK_FOLDERS

logger = logging.getLogger(__name__)

def resolve_task_folder(folder_type: str, task_data: dict):
    """
    Resolve local and ftp paths for a given folder type.
    Returns tuple (local_dir, ftp_dir, label, mode).
    """
    if folder_type not in TASK_FOLDERS:
        raise ValueError(f"Unknown folder_type: {folder_type}")
    config = TASK_FOLDERS[folder_type]
    local = config["local_key"](task_data) if callable(config["local_key"]) else task_data.get(config["local_key"])
    ftp = config["ftp_key"](task_data) if callable(config["ftp_key"]) else task_data.get(config["ftp_key"])
    return local, ftp, config["label"], config["mode"]

def download_empty_folder(task_data, fail_codes, error_codes):
    try:
        server_folder = Path(task_data.get("ftp_work_directory")).parent
        local_folder = Path(task_data.get("work_directory")).parent
        if copy_through_rclone("lsd", server_folder) == 0:
            copy_through_rclone("copy", server_folder, local_folder,
                                flags=["--exclude", "*.*", "--exclude", "**/**/", "--create-empty-src-dirs"])
    except Exception as e:
        error_codes["Copy Empty Folder"] = f"EXCEPTION: {e}"

def download_folder(folder_type: str, task_data: dict, fail_codes: dict, error_codes: dict):
    try:
        local, ftp, label, mode = resolve_task_folder(folder_type, task_data)
        os.makedirs(Path(local).parent, exist_ok=True)

        if copy_through_rclone("lsd", str(ftp)) == 0:
            status = copy_through_rclone(mode, str(ftp), str(local), flags=["--update"])
            if status != 0:
                fail_codes[label] = f"Failed to download {label}"
        else:
            fail_codes[label] = f"{label} missing on server"
    except Exception as e:
        error_codes[label] = f"EXCEPTION: {e}"

def download_dependencies(task_data, fail_codes, error_codes):
    try:
        for task in task_data.get("source_tasks_output_files_location", []):
            name = task["name"]
            ftp_output = task.get("ftp_output_directory", "").replace("\\", "/")
            local_output = task.get("local_output_directory")
            if not local_output:
                logger.warning(f"{name}: 04_Out path is empty.")
                continue

            local_dir = convert_path_for_current_os(local_output, "Heirloom")
            os.makedirs(os.path.dirname(local_dir), exist_ok=True)

            if copy_through_rclone("lsd", ftp_output) == 0:
                status = copy_through_rclone("sync", ftp_output, local_dir, flags=["--update"])
                if status != 0:
                    fail_codes[f"Download 04_Output Folder {name}"] = "Failed to download"
            else:
                fail_codes[f"Download 04_Output Folder {name}"] = "Missing on server"
    except Exception as e:
        error_codes["Download Dependencies"] = f"EXCEPTION: {e}"
