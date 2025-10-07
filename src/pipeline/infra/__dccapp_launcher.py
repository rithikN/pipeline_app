import logging
import os
import re
import subprocess
from PySide6.QtCore import QThread, Signal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from datetime import datetime
from pprint import pprint

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class FileThreadLauncher(QThread):
    """Launches a DCC application and monitors file status."""
    
    file_opened       = Signal(str)  # Emits when the file is opened
    file_closed       = Signal(str, str, str)  # Emits when the file is closed
    file_versioned_up = Signal(dict)  # Emits (old_version, new_version) on version up
    error             = Signal(str)  # Emits errors

    def __init__(self, app_path, file_path, parent=None):
        super().__init__(parent)
        self.app_path            = app_path
        self.file_path           = file_path
        self.folder_path         = os.path.dirname(file_path)
        self.file_base, self.ext = os.path.splitext(os.path.basename(file_path))
        self.version_pattern     = re.compile(r"_v(\d{3})")  # Pattern for versioning (e.g., "_v000")
        self.current_version     = self.extract_version(file_path)
        self.new_version_file    = None
        self.process             = None
        self.observer            = None
        self.running             = True
        self.was_versioned_up    = False  # Track if a version up occurred

    def extract_version(self, filename):
        """Extracts version number from the filename."""
        match = self.version_pattern.search(filename)
        return int(match.group(1)) if match else 0

    def generate_new_version_name(self, old_version, new_version):
        """Generates the correct new version filename."""
        return f"{self.file_base.replace(f"_v{old_version:03d}", f"_v{new_version:03d}")}{self.ext}"

    def run(self):
        """Launch the DCC app and start monitoring for file version changes."""
        if not os.path.exists(self.app_path):
            error_msg = f"App executable not found: {self.app_path}"
            logger.error(error_msg)
            self.error.emit(error_msg)
            return

        if not os.path.exists(self.file_path):
            error_msg = f"File not found: {self.file_path}"
            logger.error(error_msg)
            self.error.emit(error_msg)
            return

        try:
            logger.info(f"Launching {self.app_path} with file {self.file_path}")
            self.file_opened.emit(f"Opening file: {self.file_path}")

            # Launch the DCC application
            self.process = subprocess.Popen([self.app_path, self.file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Start file monitoring thread
            self.observer = Observer()
            event_handler = VersionMonitor(self)
            self.observer.schedule(event_handler, self.folder_path, recursive=False)
            self.observer.start()

            # Wait for the process to complete
            self.process.wait()

            if self.process.returncode == 0:
                if self.was_versioned_up:
                    logger.info(f"Closed file: {self.new_version_file}")
                    close_message = f"Versioned-up file closed: {self.new_version_file}"
                else:
                    logger.info(f"Closed file: {self.file_path}")
                    close_message = f"Closed file {self.file_path}"

                self.file_closed.emit(close_message, self.file_path, self.new_version_file)
            else:
                error_msg = f"App exited with errors. Return code: {self.process.returncode}"
                logger.error(error_msg)
                self.error.emit(error_msg)

        except Exception as e:
            error_msg = f"Error while launching app: {str(e)}"
            logger.exception(error_msg)
            self.error.emit(error_msg)

        finally:
            self.cleanup()

    def cleanup(self):
        """Stops the observer and marks the thread as finished."""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()

    def stop(self):
        """Force stop the monitoring process."""
        if self.process and self.process.poll() is None:
            logger.warning(f"Terminating process for file: {self.file_path}")
            self.process.terminate()
            self.process.wait()
            self.running = False
            self.file_closed.emit(f"Force-closed file: {self.file_path}")
            if self.new_version_file:
                self.file_closed.emit(f"Force-closed file: {self.new_version_file}")
        self.cleanup()


class VersionMonitor(FileSystemEventHandler):
    """
    Watches for new versions of the file being worked on.
    Detects file saves and version ups.
    """

    def __init__(self, thread_launcher):
        super().__init__()
        self.thread_launcher = thread_launcher
        self._old_version_file = None

    def on_created(self, event):
        """Check if the new file is a version up."""
        if event.is_directory:
            return

        new_file    = os.path.basename(event.src_path)
        
        if "@" in new_file:
            new_file.replace("@", "")

        new_version = self.thread_launcher.extract_version(new_file)

        if new_version > self.thread_launcher.current_version:
            # Generate correct old and new version file names
            self._old_version_file = self.thread_launcher.file_path
            
            new_version_file       = self.thread_launcher.generate_new_version_name(self.thread_launcher.current_version, new_version)

            print(f"New version detected: {new_version_file}")
            
            # new_version_up_file =  Path(os.path.join(event.src_path, new_version_file))
            # print("")
            new_version_path = event.src_path
            if "@" in new_version_path:
                new_version_path.replace("@", "")
            # print("line 147", new_version_path)
            
            new_version_path=Path(new_version_path)
            try:


            # print("line 158",new_version_path)
            # print("line 159",new_version_path.exists())

                # new_version_file  = round(os.path.getsize(new_version_path) / (1024 * 1024), 2),  # File size in MB
                version_up_data                             = dict()
                version_up_data["recent_file"]              = self._old_version_file
                version_up_data["new_file"]                 = new_version_file                    
                version_up_data["new_file_size"]            = new_version_path.stat().st_size / (1024 * 1024)
                version_up_data["new_file_last_saved_time"] = datetime.fromtimestamp(new_version_path.stat().st_mtime).strftime("%d-%m-%Y %I:%M %p")
                version_up_data["new_file_last_saved_date"] = datetime.fromtimestamp(new_version_path.stat().st_mtime).strftime("%d-%m-%Y")

                # pprint(version_up_data)
                # new_version_file_last_saved_time = datetime.fromtimestamp(new_version_path.stat().st_mtime).strftime("%d-%m-%Y %I:%M %p")



                # self.thread_launcher.file_versioned_up.emit(self._old_version_file, {"new_version_file":new_version_file, "new_version_file_size": new_version_file_size_mb, "new_version_file_last_saved_time": new_version_file_last_saved_time})
                self.thread_launcher.file_versioned_up.emit(version_up_data)
                self.thread_launcher.current_version    = new_version
                self.thread_launcher.was_versioned_up   = True
                self.thread_launcher.new_version_file   = new_version_file
                # self.thread_launcher.file_versioned_up.emit(self._old_version_file, new_version_file)
            except Exception as e:
                print(f"Exception Occurred due to {str(e)}")    