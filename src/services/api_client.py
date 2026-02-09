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

from services.auth_context import get_access_token

from pipeline.config.settings import settings
from handlers.error_handler import BackendError, MissingKeyError, handle_http_status, validate_json_keys

logger = logging.getLogger(__name__)

BASE_URL = "http://10.10.19.99:8000/api"
# BASE_URL = "http://127.0.0.1:5000/api"


def make_request(method: str, endpoint: str, data: dict | None = None,
                 required_keys: Iterable[str] | None = None, timeout: int = 10,
                 headers: dict | None = None, params: dict | None =None):

    """
    Perform an HTTP request and return JSON.
    Raises BackendError or MissingKeyError for the caller to handle.
    """
    url = f"{BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    # Redact password from logs
    safe_data = dict(data or {})
    if "password" in safe_data:
        safe_data["password"] = "***"
    logger.debug("HTTP %s %s data=%s", method, url, safe_data)

    req_headers = {"Accept": "application/json"}
    if headers:
        req_headers.update(headers)

    token = get_access_token()
    if token and "Authorization" not in req_headers:
        req_headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.request(
            method,
            url,
            json=data,
            params=params,
            headers=req_headers,
            allow_redirects=False,
            timeout=timeout,
        )

        if resp.status_code != 200:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            raise BackendError(
                f"HTTP {resp.status_code}: {body}",
                status_code=resp.status_code
            )

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


def fetch_data(endpoint: str, required_keys: Iterable[str] | None = None, headers: dict | None = None, params: dict | None = None):
    """GET wrapper."""
    return make_request("GET", endpoint, required_keys=required_keys, headers=headers, params=params)


def send_data(endpoint: str, data: dict, required_keys: Iterable[str] | None = None, headers: dict | None = None):
    """POST wrapper."""
    return make_request("POST", endpoint, data=data, required_keys=required_keys, headers=headers)
