"""
file_ops.py
------------
Local filesystem helpers for data_service.
Handles collecting, validating, and versioning work files.
"""

import re
import logging
from datetime import datetime
from pathlib import Path
from services.constants import EXCLUDE_MAC_FILES
from pipeline.config.settings import SYSTEM

logger = logging.getLogger(__name__)


def collect_local_files(task: dict) -> list[Path]:
    """
    Return all valid local work files under the task directory.
    """
    task_dir = Path(task.get("work_directory", ""))
    if not task_dir.exists():
        logger.debug("Task dir not found: %s", task_dir)
        return []
    return [
        f for f in task_dir.iterdir()
        if f.is_file() and f.suffix not in (".txt", ".blend1", ".log")
    ]


def handle_version_up(file_path: Path, task_info: dict) -> dict | None:
    """
    Create a new version record for an unsynced file.
    Returns dict or None if pattern/app not matched.
    """
    file_name = file_path.name
    file_ext = file_path.suffix.lower()
    version_match = re.search(r'_v(\d+)', file_name)
    version = f"V{int(version_match.group(1)):03}" if version_match else "V001"

    app_info = task_info.get("dcc_app", {})
    if not app_info or app_info == "App Not Found/Installation not exists!":
        return None

    pattern = r"^HL_Sc\d{4}_Sh\d{4}[A-Z]?_[A-Z]+_v\d{3}\.[a-zA-Z0-9]+$"
    if not re.match(pattern, file_name):
        return None
    if file_ext not in app_info.get("output_format", []):
        return None

    entry = {
        "app_name": app_info["app_name"],
        "file_size": round(file_path.stat().st_size / (1024 * 1024), 2),
        "version": version,
        "status": "in_progress",
        "date": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%d-%m-%Y"),
        "slug": None,
        "work_detail": {
            "file_name": file_name,
            "file_type": f"{app_info['app_name']} / {file_ext.upper()}",
            "last_saved": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%d-%m-%Y %I:%M %p"),
            "locked_status": "Unlocked",
            "work_file": file_path.as_posix(),
            "app_executable_path": (
                app_info["mac_executable_path"] if SYSTEM == "Darwin" else app_info["app_executable_path"]
            ), #ToDO logic should be in config
            "preview_path": "N/A",
            "local_preview_path": "",
            "preview_formats": task_info.get("preview_formats", []),
        },
        "preview_detail": {"preview_path": "", "local_preview_path": ""},
    }
    return entry


def sync_local_files(task: dict) -> list[dict]:
    """
    Returns a combined list of server + local un-synced work_files.
    """
    from copy import deepcopy
    task_copy = deepcopy(task)
    local_files = collect_local_files(task_copy)
    existing_versions = [f["work_detail"]["file_name"] for f in task_copy.get("work_files", [])]

    for file_path in local_files:
        if file_path.name in EXCLUDE_MAC_FILES:
            continue
        if file_path.name not in existing_versions:
            new_entry = handle_version_up(file_path, task_copy)
            if new_entry:
                task_copy.setdefault("work_files", []).append(new_entry)
    return task_copy.get("work_files", [])
