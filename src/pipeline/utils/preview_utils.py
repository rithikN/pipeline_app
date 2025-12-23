# pipeline/utils/preview_utils.py
from pathlib import Path

def verify_and_return_preview_file(current_working_version, preview_file_name, *args, **kwargs):
    """
    Verify existence of a preview file in the current working version's preview directory.

    Args:
        current_working_version (dict): The current working version metadata.
        preview_file_name (str): Base name of the preview file (without extension).

    Returns:
        tuple: (Path to preview file, resolution) or (None, None) if not found.
    """
    if "preview_directory" in current_working_version:
        local_preview_directory = Path(current_working_version["preview_directory"])
        supported_preview_formats = current_working_version["work_detail"].get("preview_formats", [])
        preview_file_path, template_file_resolution = None, None

        for prv_frmt in supported_preview_formats:
            for file_type, resolution in prv_frmt.items():
                candidate = local_preview_directory / f"{preview_file_name}.{file_type}"
                if candidate.exists():
                    return candidate, resolution

    return None, None
