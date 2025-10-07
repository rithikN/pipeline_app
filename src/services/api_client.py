"""
api_client.py
--------------
Thin HTTP client used by data_service.
No UI, no dialogs — only raises or returns data.
"""

import logging
import requests
from typing import Iterable
from requests.exceptions import RequestException, Timeout, ConnectionError

from pipeline.config.settings import settings
from handlers.error_handler import BackendError, MissingKeyError, handle_http_status, validate_json_keys

logger = logging.getLogger(__name__)

BASE_URL = settings.get("API_BASE_URL", "http://127.0.0.1:5000/api")


def make_request(method: str, endpoint: str, data: dict | None = None,
                 required_keys: Iterable[str] | None = None, timeout: int = 10):
    """
    Perform an HTTP request and return JSON.
    Raises BackendError or MissingKeyError for the caller to handle.
    """
    url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    logger.debug("HTTP %s %s data=%s", method, url, data)
    try:
        resp = requests.request(
            method,
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            allow_redirects=True,
            timeout=timeout,
        )

        if resp.status_code != 200:
            handle_http_status(resp, url)
            raise BackendError(f"HTTP {resp.status_code}: {resp.reason}", status_code=resp.status_code)

        payload = resp.json()
        validate_json_keys(payload, required_keys, endpoint)
        return payload

    except (BackendError, MissingKeyError):
        raise
    except ConnectionError as e:
        logger.error("Connection error contacting backend: %s", e)
        return None
    except Timeout:
        logger.warning("Request timed out: %s", url)
        return None
    except RequestException as e:
        raise BackendError(f"Request error: {e}") from e
    except Exception as e:
        raise BackendError(f"Unexpected error: {e}") from e


def fetch_data(endpoint: str, required_keys: Iterable[str] | None = None):
    """GET wrapper."""
    return make_request("GET", endpoint, required_keys=required_keys)


def send_data(endpoint: str, data: dict, required_keys: Iterable[str] | None = None):
    """POST wrapper."""
    return make_request("POST", endpoint, data=data, required_keys=required_keys)
