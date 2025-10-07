import os, re
from pathlib import Path, PureWindowsPath
from pipeline.config.settings import SYSTEM

def split_from_version_simple(filename: str) -> tuple[str, str]:
    """Split a filename into base + version suffix."""
    match = re.search(r"_v\d{3}", filename)
    if match:
        index = match.start()
        return filename[:index], filename[index:]
    return filename, ""

def convert_path_for_current_os(input_path_str: str, project_name: str) -> str | None:
    """
    Converts a given project path to the canonical format for the current OS.
    Assumes the path contains `project_name` as a directory.
    """
    try:
        p_input = PureWindowsPath(input_path_str)
        input_parts = p_input.parts
    except Exception as e:
        return f"ERROR: Could not parse input path '{input_path_str}' with pathlib: {e}"

    try:
        project_name_idx = input_parts.index(project_name)
    except ValueError:
        return f"ERROR: Project name '{project_name}' not found in '{input_path_str}'."

    relative_to_project_root_parts = input_parts[project_name_idx:]

    if SYSTEM == "Windows":
        base_path = Path("D:/")
    elif SYSTEM == "Darwin":
        base_path = Path.home() / "Documents"
    else:
        return f"ERROR: '{SYSTEM}' OS not supported for path conversion."

    return str(base_path.joinpath(*relative_to_project_root_parts))
