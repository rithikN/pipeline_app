# pipeline/infra/rclone.py

import os
import logging
import subprocess
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from pipeline.config.settings import settings

logger = logging.getLogger(__name__)


def get_rclone_path() -> Path:
    """
    Returns the path to rclone binary depending on the OS.
    """
    candidate_paths = settings["RCLONE_PATHS"]
    for rclone_path in candidate_paths:
        if os.path.exists(rclone_path):
            return Path(rclone_path)

    raise FileNotFoundError(f"rclone executable not found for {SYSTEM}")


def copy_through_rclone(rclone_command="copyto", src="", dest="", flags=None) -> int:
    """
    Run a blocking rclone command (copy, sync, etc.) and return its exit code.

    Args:
        rclone_command (str): rclone subcommand (copy, sync, check, etc.)
        src (str): source path
        dest (str): destination path (optional for commands like 'lsd')
        flags (list[str], optional): extra rclone flags

    Returns:
        int: process return code (0 = success)
    """
    rclone_path = get_rclone_path()
    if not os.path.exists(rclone_path):
        error_message = f"copy_through_rclone : rclone not found at {rclone_path}"
        logger.error(error_message)
        return -1

    flags = flags or []

    try:
        if rclone_command in ["copy", "sync"]:
            flags.extend(["--exclude", ".DS_Store"])

        if not dest:
            # Commands like "lsd" only need src
            process = [rclone_path.as_posix(), rclone_command, src]
        else:
            process = [
                rclone_path.as_posix(),
                rclone_command,
                src,
                dest,
                "--progress",
                "--progress-terminal-title",
            ]
            process.extend(flags)

        logger.info("Running rclone: %s", " ".join(process))
        result = subprocess.run(process, text=True)
        return result.returncode

    except Exception as e:
        logger.exception("Exception in copy_through_rclone")
        return -1


class RcloneWorker(QThread):
    """
    Runs the rclone process in a QThread and emits progress, finished, and error signals.
    """

    progress_signal = Signal(int)   # Emits progress percentage
    finished_signal = Signal(int)   # Emits exit status code
    error_signal = Signal(str)      # Emits error messages

    def __init__(self, rclone_command: str, src: str, dest: str, flags=None, parent=None):
        super().__init__(parent)
        self.rclone_command = rclone_command
        self.src = src
        self.dest = dest
        self.flags = flags or []
        self.status_code = -1
        self.process: subprocess.Popen | None = None

    def run(self):
        rclone_path = get_rclone_path()
        if not os.path.exists(rclone_path):
            error_message = f"Rclone not found: {rclone_path}"
            logger.error(error_message)
            self.error_signal.emit(error_message)
            self.finished_signal.emit(-1)
            return

        try:
            # Add safe default flags
            if self.rclone_command in ["copy", "sync"]:
                self.flags.extend(["--exclude", ".DS_Store"])

            cmd = [
                rclone_path.as_posix(),
                self.rclone_command,
                self.src,
                self.dest,
                "--progress",
                "--progress-terminal-title",
            ]
            cmd.extend(self.flags)

            logger.info("Executing: %s", " ".join(cmd))
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
            )

            for line in self.process.stdout:
                if "%" in line:
                    percent = self.extract_progress(line)
                    if percent is not None:
                        self.progress_signal.emit(percent)

            self.process.wait()
            self.status_code = self.process.returncode

            if self.status_code != 0:
                err_output = self.process.stderr.read()
                self.error_signal.emit(err_output)

            self.finished_signal.emit(self.status_code)

        except Exception as e:
            logger.exception("Exception in RcloneWorker")
            self.error_signal.emit(str(e))
        finally:
            self.process = None

    def cancel(self):
        """Terminate the running rclone process."""
        if self.process and self.process.poll() is None:
            logger.warning("Terminating rclone process...")
            self.process.terminate()

    @staticmethod
    def extract_progress(output_line: str) -> int | None:
        """Parse progress percentage from rclone output."""
        try:
            for part in output_line.split():
                if "%" in part:
                    return int(part.strip("%"))
        except ValueError:
            return None
        return None
