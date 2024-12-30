import requests
from services.constants import (
    TASK_NAME, TASK_STATUS, USERNAME, DATE, COMMENT, STATUS_COLOR,
    WORK_APP, WORK_VERSION, WORK_SIZE, WORK_DATE, PREVIEW_PATH,
    TYPE, LABEL, ID, FIELD_TYPE
)
from ui.managers.message_box_manager import MessageBoxManager
from handlers.error_handler import (
    BackendError,
    MissingKeyError,
    handle_http_status,
    validate_json_keys
)

BASE_URL = "http://127.0.0.1:5000/api"


def make_request(method, endpoint, data=None, required_keys=None):
    """
    Generic function for making API requests.

    Args:
        method (str): HTTP method (GET, POST, etc.)
        endpoint (str): API endpoint relative to the base URL.
        data (dict): Payload to send with the request.
        required_keys (list): Keys expected in the response.

    Returns:
        dict: JSON response from the server.

    Raises:
        BackendError: For HTTP or connection errors.
        MissingKeyError: If required keys are missing in the response.
    """
    try:
        url = f"{BASE_URL}/{endpoint}"
        response = requests.request(
            method,
            url,
            json=data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code != 200:
            handle_http_status(response, url)

        json_data = response.json()
        validate_json_keys(json_data, required_keys, endpoint)
        return json_data

    except BackendError as be:
        MessageBoxManager.show_error(be.message)
        raise
    except MissingKeyError as mke:
        MessageBoxManager.show_error(mke.message)
        raise
    except requests.RequestException as req_err:
        error_message = f"Request error occurred: {req_err}\n Check backend!"
        MessageBoxManager.show_error(error_message)
        raise BackendError(error_message) from req_err
    except Exception as ex:
        error_message = f"An unexpected error occurred: {ex}"
        MessageBoxManager.show_error(error_message)
        raise BackendError(error_message) from ex


# Common functions to send and fetch data
def fetch_data(endpoint, required_keys=None):
    """
    Fetch data from the given endpoint.
    """
    return make_request("GET", endpoint, required_keys=required_keys)


def send_data(endpoint, data, required_keys=None):
    """
    Send data to the given endpoint.
    """
    return make_request("POST", endpoint, data=data, required_keys=required_keys)


# Specific API functions
def login_user(credentials):
    """
    Login the user with provided credentials.
    Args:
        credentials (dict): Must include 'username' and 'password'.
    Returns:
        dict: Response containing login status.
    Notes for backend:
        Ensure the response includes the 'status' key.
    """
    return send_data("auth/login", credentials, required_keys=["status"])


def get_formUiData():
    """
    Fetch UI form data configuration.
    Returns:
        list: List of form elements with 'id', 'label', 'options', and 'type'.
    """
    return fetch_data("formUiData", required_keys=[TYPE, LABEL, ID, TYPE])


def get_projects(data):
    """
    Fetch projects based on user details.
    Args:
        data (dict): Must include 'username', 'location', and 'work_mode'.
    Returns:
        list: List of projects.
    """
    return send_data("projects", data)


# Functions for specific hierarchical data
def get_episodes(project_name):
    return send_data("episodes", {"project_name": project_name})


def get_scenes(project_name):
    return send_data("scenes", {"project_name": project_name})


def get_tasks(project_name):
    return send_data("tasks", {"project_name": project_name})


# Work file-related operations
def get_workFiles(data):
    """
    Fetch work files related to a task.
    Args:
        data (dict): Should include required filters or task info.
    """
    return send_data("workFiles", data, required_keys=[
        WORK_APP, WORK_VERSION, WORK_SIZE, WORK_DATE
    ])


def get_workDetails(data):
    """
    Fetch work file details.
    Args:
        data (dict): Includes task-related file metadata.
    """
    return send_data("workDetails", data, required_keys=[PREVIEW_PATH])


def get_fileDetails(data):
    """
    Fetch specific file details.
    """
    return send_data("fileDetails", data, required_keys=[PREVIEW_PATH])


# Task and log-related operations
def get_taskDetail(task_data):
    return send_data("TaskDetail", task_name, required_keys=[PREVIEW_PATH])


def get_taskLog(task_name):
    return send_data("TaskLog", task_name, required_keys=[
        TASK_STATUS, USERNAME, DATE, COMMENT, STATUS_COLOR
    ])


def get_taskData(data):
    return send_data("taskData", data, required_keys=[TASK_NAME, TASK_STATUS])


def get_taskStatus(data):
    return send_data("taskStatus", data)


# Additional notes for backend
"""
- UI will pass the required arguments in the request payload as JSON.
- Ensure responses include required keys mentioned in `required_keys` argument for each function.
- Response keys can be updated in the `constants.py` file for consistent mapping.
- Inform if additional arguments are needed for any endpoint.
"""
