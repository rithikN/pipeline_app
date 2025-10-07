"""
pipeline/domain/task_folders.py

Canonical task folder definitions.
Keeps folder rules centralized so controllers don’t hardcode paths.
"""

from pathlib import Path

TASK_FOLDERS = {
    "input": {
        "label": "00_Input Folder",
        "local_key": "input_directory",
        "ftp_key": "ftp_input_directory",
        "mode": "copy",
    },
    "feedback": {
        "label": "03_Feedback Folder",
        "local_key": "feedback_directory",
        "ftp_key": "ftp_feedback_directory",
        "mode": "copy",
    },
    "references": {
        "label": "99_Brief & References",
        "local_key": lambda task: Path(task["work_directory"]).parent.parent / "99_Brief & References",
        "ftp_key": lambda task: Path(task["ftp_work_directory"]).parent.parent / "99_Brief & References",
        "mode": "sync",
    },
}
