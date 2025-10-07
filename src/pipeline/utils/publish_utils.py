from pathlib import Path

def verify_and_return_publish_format(current_working_version: dict, preview_file_name: str):
    """
    Find the matching publish format resolution for a given preview file.
    """
    supported_formats = current_working_version["work_detail"]["publish_formats"]
    preview_file_ext = Path(preview_file_name).suffix

    for frmt in supported_formats:
        for file_type, resolution in frmt.items():
            if file_type in preview_file_ext:
                return resolution
    return None
