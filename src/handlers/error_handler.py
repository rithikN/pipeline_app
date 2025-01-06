import logging, pprint
from collections.abc import Mapping, Sequence
from ui.managers.message_box_manager import MessageBoxManager

logger = logging.getLogger(__name__)


class BackendError(Exception):
    """Custom exception for backend (HTTP) errors."""

    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class MissingKeyError(Exception):
    """Custom exception for missing keys in a JSON payload."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def handle_http_status(response, url=None):
    """
    Handle specific HTTP status codes and show a message box.
    This function can either raise exceptions or simply show
    a message box, depending on your design preference.
    """
    status_messages = {
        400: "Bad Request. Please check your input.",
        401: "Unauthorized. Invalid credentials or session expired.",
        403: "Forbidden. You do not have access to this resource.",
        404: f"Not Found. The requested resource was not found at {url}.",
        500: "Internal Server Error. Please try again later.",
    }

    # For this example, we show a MessageBox on each known error
    if response.status_code in status_messages:
        message = status_messages[response.status_code]
        if response.status_code == 404 and url:
            message = f"Not Found. The resource '{url}' was not found."
        MessageBoxManager.show_error(f"Backend Error: {message}")

    elif 400 <= response.status_code < 500:
        MessageBoxManager.show_error(f"Backend Error: Client Error. {response.status_code} {response.reason}")

    elif response.status_code >= 500:
        MessageBoxManager.show_error(f"Backend Error: Server Error. {response.status_code} {response.reason}")


def truncate_json(data, max_length=500):
    """
    Truncate large JSON data for display while keeping it readable.

    Args:
        data (any): The JSON data to truncate.
        max_length (int): Maximum length of the string representation.

    Returns:
        str: Truncated string representation of the data.
    """
    pretty_data = pprint.pformat(data, width=80, compact=True)
    if len(pretty_data) > max_length:
        return pretty_data[:max_length] + "...\n[Truncated]"
    return pretty_data


def validate_json_keys(json_data, required_keys, endpoint, max_display_length=500):
    """
    Checks if all required_keys are present in the given json_data.
    Handles nested dictionaries and lists of dictionaries based on a dot-separated key path.
    Raises MissingKeyError if any required key is missing.

    Args:
        json_data (dict or list): The JSON data to validate.
        required_keys (list): List of required keys or key paths to check for (dot-separated).
        endpoint (str): The API endpoint for context in error messages.
        max_display_length (int): Maximum length of the truncated data for display.

    Raises:
        MissingKeyError: If any required key is missing.
    """
    if not required_keys:
        return  # No required keys to check

    def check_key_path(data, key_path):
        """
        Recursively check if a key path exists in the data.

        Args:
            data (dict or list): The JSON data to check.
            key_path (str): Dot-separated path of keys to check.

        Returns:
            bool: True if the key path exists, False otherwise.
        """
        keys = key_path.split(".")
        current_data = data
        for key in keys:
            if isinstance(current_data, list):
                # If it's a list, check each element for the next key
                if not all(check_key_path(item, ".".join(keys)) for item in current_data if isinstance(item, dict)):
                    return False
                return True
            elif isinstance(current_data, dict):
                # If it's a dictionary, check for the key
                if key not in current_data:
                    return False
                current_data = current_data[key]
            else:
                return False
        return True

    missing_keys = []
    for key_path in required_keys:
        if not check_key_path(json_data, key_path):
            missing_keys.append(key_path)

    if missing_keys:
        # Format and truncate the data for display
        truncated_data = truncate_json(json_data, max_display_length)
        msg = (
            f"Missing keys in response from '{endpoint}': {', '.join(missing_keys)}. "
            f"Received data:\n{truncated_data}"
        )
        # Show truncated data in the MessageBox
        # MessageBoxManager.show_error(msg)

        # Log full data to the console using pprint
        logger.error(f"Full data for debugging from '{endpoint}':")
        pprint.pprint(json_data, width=120)

        # Raise the exception with the full message
        raise MissingKeyError(msg)


def truncate_json_pretty(data, max_length=500):
    """
    Truncate large JSON data for display while keeping it readable and formatted with HTML.

    Args:
        data (any): The JSON data to truncate.
        max_length (int): Maximum length of the string representation.

    Returns:
        str: Truncated and formatted string representation of the data in HTML.
    """
    import json
    formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
    if len(formatted_json) > max_length:
        truncated = formatted_json[:max_length] + "\n...\n[Truncated]"
    else:
        truncated = formatted_json

    # Wrap the formatted JSON in a <pre> tag for better readability
    return f"<pre style='font-family: Consolas, monospace; font-size: 12px;'>{truncated}</pre>"


def validate_json_keys1(json_data, required_keys, endpoint, max_display_length=500):
    """
    Checks if all required_keys are present in the given json_data.
    Handles nested dictionaries and lists of dictionaries based on a dot-separated key path.
    Raises MissingKeyError if any required key is missing.

    Args:
        json_data (dict or list): The JSON data to validate.
        required_keys (list): List of required keys or key paths to check for (dot-separated).
        endpoint (str): The API endpoint for context in error messages.
        max_display_length (int): Maximum length of the truncated data for display.

    Raises:
        MissingKeyError: If any required key is missing.
    """
    if not required_keys:
        return  # No required keys to check


    def check_key_path(data, key_path):
        """
        Recursively check if a key path exists in the data.

        Args:
            data (dict or list): The JSON data to check.
            key_path (str): Dot-separated path of keys to check.

        Returns:
            bool: True if the key path exists, False otherwise.
        """
        keys = key_path.split(".")
        current_data = data
        for key in keys:
            if isinstance(current_data, list):
                # If it's a list, check each element for the next key
                if not all(check_key_path(item, ".".join(keys)) for item in current_data if isinstance(item, dict)):
                    return False
                return True
            elif isinstance(current_data, dict):
                # If it's a dictionary, check for the key
                if key not in current_data:
                    return False
                current_data = current_data[key]
            else:
                return False
        return True

    missing_keys = []
    for key_path in required_keys:
        if not check_key_path(json_data, key_path):
            missing_keys.append(key_path)

    if missing_keys:
        # Truncate and format the JSON data
        truncated_data_html = truncate_json_pretty(json_data, max_display_length)
        msg = (
            f"<b>Error:</b> Missing keys in response from '<i>{endpoint}</i>': "
            f"<span style='color: red;'>{', '.join(missing_keys)}</span>.<br>"
            f"<b>Received data:</b><br>{truncated_data_html}"
        )
        raise MissingKeyError(msg)


if __name__ == '__main__':
    json_data = [
        {
            "name": "HL_BGL_Sc0910_Sh0010",
            "shot_detail": {
                "artist_assigned": {"employee": {"employee_name": "John Doe"}},
                "status": "Not Started",
            },
            "status": "not_started",
        },
        {
            "name": "HL_BGL_Sc9999_Sh9990",
            "artist_assigned": {
                "artist_assigned": {"employee": {"employee_name": "Jane Doe"}},
                "status": "Completed",
            },
            "status": "not_started",
        },
    ]

    required_keys = ["name", "shot_detail", "artist_assigned", "employee_name", "status"]
    endpoint = "taskData"
    json_data = [
        {'id': 'location', 'label': 'Select Office Location', 'options': ['Pune', 'Thrissur'], 'type': 'combobox'},
        {'id': 'work_mode', 'label': 'Select Work Mode', 'options': ['Office', 'Work from Home'], 'type': 'combobox'}]
    validate_json_keys(json_data, required_keys, endpoint)
