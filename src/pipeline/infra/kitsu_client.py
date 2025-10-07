# pipeline/infra/kitsu_client.py

import logging
import requests

from pipeline.config.settings import settings

logger = logging.getLogger(__name__)


def fetch_data_from_kitsu(payload: dict) -> dict:
    """
    Fetch shot/asset data from the Kitsu API.

    Args:
        payload (dict): JSON payload to send.

    Returns:
        dict: Parsed JSON response.
    """
    try:
        url = f"{settings.KITSU_API_URL}/fetch"  # <--- configurable
        headers = {"Authorization": f"Bearer {settings.KITSU_API_TOKEN}"}

        logger.debug("Fetching data from Kitsu: %s", url)
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    except Exception as e:
        logger.error(f"Kitsu API request failed: {e}", exc_info=True)
        return {"error": str(e)}
