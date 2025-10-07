from PySide6.QtCore import QObject, Signal, QThread
import subprocess

class FileLauncherThread(QThread):
    """
    Thread to handle the subprocess of launching a file and detecting when it is closed.
    """
    file_closed = Signal(str)

    def __init__(self, app_path, file_path, file_key):
        super().__init__()
        self.app_path = app_path
        self.file_path = file_path
        self.file_key = file_key

    def run(self):
        try:
            process = subprocess.Popen([self.app_path, self.file_path])
            process.wait()  # Wait until the process is closed
            self.file_closed.emit(self.file_key)  # Emit signal when the file is closed
        except Exception as e:
            print(f"Error launching file: {e}")