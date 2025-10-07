"""
data_service.py
---------------
High-level data layer.
Handles API endpoints + local file sync helpers.
No UI or dialogs here.
"""

import logging
import socket
from pipeline.config.settings import settings, PIPELINE_ENV
from services.api_client import fetch_data, send_data
from services.file_ops import sync_local_files
from pipeline.infra.rclone import copy_through_rclone

from services.constants import (
    PROJECT_NAME,
    TASK_STATUS, TASK_STATUS_NAME, TASK_STATUS_COLOR,
    TASK_SHOT_DETAIL, TASK_SHOT_SEQ_DETAIL, TASK_SHOT_SEQ_EPISODE_DETAIL,
    TASK_SHOT_SEQ_EPISODE_NAME, TASK_SHOT_SEQ_NAME
)

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------------
BASE_URL = settings.get("API_BASE_URL", "http://127.0.0.1:5000/api")


# -------------------------------------------------------------------------
# API ENDPOINT WRAPPERS
# -------------------------------------------------------------------------
def login_user(credentials):
    return send_data("auth/login/", credentials, required_keys=["status"])


def get_formUiData():
    return fetch_data("formUiData", required_keys=["type", "label", "id"])


def get_projects(data):
    return send_data("projects", data)


def get_taskData(data):
    return send_data("api/tasks/", data)


def get_taskDetail(task_name, task_list):
    for task in task_list:
        if task_name == task["name"]:
            return task


def get_taskTypes(task_list):
    return [task.get("task_type") for task in task_list if "task_type" in task]


def get_taskStatus(task_list):
    """
    Build a map like {"IN_PROGRESS": "#ffaa00", "APPROVED": "#00ff88", ...}
    using constant keys from services.constants.
    """
    status_map = {}
    for task in task_list:
        status_obj = task.get(TASK_STATUS) or {}
        name = (status_obj.get(TASK_STATUS_NAME) or "").upper()
        color = status_obj.get(TASK_STATUS_COLOR)
        if name:
            status_map[name] = color
    return status_map



def get_episodes(project_data, task_list):
    """
    Returns: { <project_name>: [episode_name, episode_name, ...] }
    Uses constant keys for nested traversal.
    """
    project_name = project_data.get(PROJECT_NAME)
    episodes = [
        task.get(TASK_SHOT_DETAIL, {})
            .get(TASK_SHOT_SEQ_DETAIL, {})
            .get(TASK_SHOT_SEQ_EPISODE_DETAIL, {})
            .get(TASK_SHOT_SEQ_EPISODE_NAME)
        for task in task_list
        if task.get(TASK_SHOT_DETAIL, {}).get(TASK_SHOT_SEQ_DETAIL, {}).get(TASK_SHOT_SEQ_EPISODE_DETAIL)
    ]
    return {project_name: episodes}



def get_scenes(task_list):
    """
    Returns a flat list of sequence/scene names for the task list.
    Uses constant keys for nested traversal.
    """
    return [
        task.get(TASK_SHOT_DETAIL, {})
            .get(TASK_SHOT_SEQ_DETAIL, {})
            .get(TASK_SHOT_SEQ_NAME)
        for task in task_list
        if task.get(TASK_SHOT_DETAIL, {}).get(TASK_SHOT_SEQ_DETAIL)
    ]



# -------------------------------------------------------------------------
# WORK FILES / LOCAL SYNC
# -------------------------------------------------------------------------
def get_workFiles(task_name, task_data):
    return sync_local_files(task_data)


def get_workDetails(work_file):
    """Return work file details."""
    return work_file


# -------------------------------------------------------------------------
# PIPELINE ACTIONS
# -------------------------------------------------------------------------
def create_file(data):
    return send_data("api/create-file-record/", data)


def version_up_file(data):
    return send_data("api/file/version_up/", data)


def upload_to_kitsu(data):
    return send_data("api/upload-to-kitsu/", data)


def fetch_data_from_kitsu(data):
    return send_data("api/fetch-data-from-kitsu/", data)


def publish_file(data):
    return send_data("api/file/publish/", data)


# -------------------------------------------------------------------------
# NETWORK / VPN / FTP CHECKS
# -------------------------------------------------------------------------
def check_internet_connection(timeout=3):
    """Check if internet (Google DNS) is reachable."""
    host, port = "8.8.8.8", 53
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((host, port))
        return True
    except socket.error:
        return False


def check_VPN_connection(check_NET=True, timeout=3):
    """Check VPN by calling the backend health endpoint."""
    if PIPELINE_ENV == "local":
        logger.debug("[Mock VPN] Skipping VPN check in local mode.")
        return True
    response = fetch_data("api/check-connection/")
    if response:
        return True
    if check_NET and not check_internet_connection(timeout=timeout):
        return False
    return False


def check_ftp_connection(check_RCLONE=False, check_FTP_conn=False, check_NET=True, timeout=3):
    """Verify FTP / Rclone connectivity."""
    if PIPELINE_ENV == "local":
        logger.debug("[Mock FTP] Skipping FTP check in local mode.")
        return True
    ftp_status = copy_through_rclone("lsd", src="hlm:/Heirloom_Server")
    if check_RCLONE and "FileNotFoundError" in str(ftp_status):
        return False
    if check_FTP_conn and ftp_status != 0:
        if check_NET and not check_internet_connection(timeout=timeout):
            return False
        return None
    return True

# Additional notes for backend
"""
- UI will pass the required arguments in the request payload as JSON.
- Ensure responses include required keys mentioned in `required_keys` argument for each function.
- Response keys can be updated in the `constants.py` file for consistent mapping.
- Inform if additional arguments are needed for any endpoint.
"""
