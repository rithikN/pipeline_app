
"""
pipeline/config/settings.py
------------
Centralized configuration loader for the pipeline.
Loads:
- environment.yaml → per-environment infra config
- dcc_apps.yaml → list of available DCC applications
"""

import os
import yaml
import platform
import logging.config
from pathlib import Path
from dotenv import load_dotenv

# ------------------------------------------------------------
# BASE PATHS & ENVIRONMENT
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)
PIPELINE_ENV = os.getenv("PIPELINE_ENV", "default")
SYSTEM = platform.system()

# ------------------------------------------------------------
# LOAD YAML FILES
# ------------------------------------------------------------
with open(CONFIG_DIR / "environment.yaml", "r") as f:
    ENV_CONFIG = yaml.safe_load(f)

with open(CONFIG_DIR / "dcc_apps.yaml", "r") as f:
    DCC_APPS = yaml.safe_load(f)

# Merge environment-specific config
ACTIVE_CONFIG = {**ENV_CONFIG.get("default", {}), **ENV_CONFIG.get(PIPELINE_ENV, {})}

# ------------------------------------------------------------
# CONFIG VARIABLES
# ------------------------------------------------------------
KITSU_BASE_URL = ACTIVE_CONFIG["KITSU_BASE_URL"]
KITSU_TIMEOUT = ACTIVE_CONFIG.get("KITSU_TIMEOUT", 15)
ASSET_SERVER_BASE = ACTIVE_CONFIG["ASSET_SERVER_BASE"]
DEBUG_MODE = ACTIVE_CONFIG.get("PIPELINE_DEBUG", False)
RCLONE_PATHS = ACTIVE_CONFIG.get("RCLONE_PATHS", {}).get(SYSTEM, [])
THUMBNAIL_PATH = ACTIVE_CONFIG.get("THUMBNAIL_PATH", {}).get(SYSTEM)

# Unified settings dictionary
settings = {
    "PIPELINE_ENV": PIPELINE_ENV,
    "SYSTEM": SYSTEM,
    "KITSU_BASE_URL": KITSU_BASE_URL,
    "KITSU_TIMEOUT": KITSU_TIMEOUT,
    "ASSET_SERVER_BASE": ASSET_SERVER_BASE,
    "DEBUG_MODE": DEBUG_MODE,
    "RCLONE_PATHS": RCLONE_PATHS,
    "APPLICATIONS": DCC_APPS,
    "THUMBNAIL_PATH": THUMBNAIL_PATH,
}

# ------------------------------------------------------------
# LOGGING
# ------------------------------------------------------------
def setup_logging():
    """Setup unified logging for the pipeline."""
    log_dir = BASE_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {"format": "%(levelname)s - %(name)s - %(message)s"},
            "detailed": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(funcName)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
                "level": "DEBUG" if DEBUG_MODE else "INFO",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_dir / "app.log"),
                "maxBytes": 5_000_000,
                "backupCount": 3,
                "formatter": "detailed",
                "level": "DEBUG" if DEBUG_MODE else "INFO",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG_MODE else "INFO",
        },
    }

    logging.config.dictConfig(LOGGING_CONFIG)
    logging.getLogger(__name__).info(
        f"Pipeline config loaded (env={PIPELINE_ENV}, system={SYSTEM}, debug={DEBUG_MODE})"
    )


def get_setting(key: str, default=None):
    """Safely retrieve a config setting."""
    return settings.get(key, default)
