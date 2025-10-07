# pipeline/infra/paths.py

import logging
from pathlib import Path, PureWindowsPath
from pipeline.config.settings import SYSTEM

logger = logging.getLogger(__name__)


def convert_path_for_current_os(input_path_str: str, project_name: str) -> str | None:
    """
    Converts a given project path to the canonical format for the current OS.
    It assumes the path contains `project_name` as a directory.
    """
    try:
        p_input = PureWindowsPath(input_path_str)
        input_parts = p_input.parts
    except Exception as e:
        error_message = f"ERROR: Could not parse input path '{input_path_str}' with pathlib: {e}"
        logger.error(error_message)
        return None

    try:
        project_name_idx = input_parts.index(project_name)
    except ValueError:
        error_message = f"ERROR: Project name '{project_name}' not found in '{input_path_str}'."
        logger.error(error_message)
        return None

    relative_to_project_root_parts = input_parts[project_name_idx:]

    # ToDo logic should be in config
    if SYSTEM == "Windows":
        base_path = Path("D:/")
        final_path = base_path.joinpath(*relative_to_project_root_parts)
    elif SYSTEM == "Darwin":
        home_dir = Path.home()
        base_path = home_dir / "Documents"
        final_path = base_path.joinpath(*relative_to_project_root_parts)
    else:
        error_message = f"ERROR: '{SYSTEM}' OS not supported for path conversion."
        logger.error(error_message)
        return None

    return str(final_path)
