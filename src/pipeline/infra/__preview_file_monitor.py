import os
import logging
from PySide6.QtCore import QObject, Signal, QThread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PreviewFileMonitor(QObject, FileSystemEventHandler):
    """
    Watches for new JPEG files being saved inside a monitored folder
    and emits a signal when detected.
    """
    jpeg_detected = Signal(str)
    # Signal that emits file path when a JPEG is saved
    def __init__(self, monitored_folder):
        super().__init__()
        self.monitored_folder = monitored_folder

    def on_created(self, event):
        """Triggers when a file is created in the monitored folder."""
        if event.is_directory:
            return
        # Ignore directories
        file_extension = os.path.splitext(event.src_path)[1].lower()
        # Check if it's a JPEG file
        if file_extension in [".jpeg", ".jpg"]:
            logger.info(f"New JPEG file detected: {event.src_path}")
            # Emit the signal with file path
            self.jpeg_detected.emit(event.src_path)


class PreviewMonitorThread(QThread):
    """
    Runs the Watchdog observer in a separate thread to prevent blocking the UI.
    """
    jpeg_detected = Signal(str)  # Signal to forward file path to UI
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.observer = Observer()

    def run(self):
        """Starts the watchdog observer in a separate thread."""
        event_handler = JpegFileMonitor(self.folder_path)
        event_handler.jpeg_detected.connect(self.jpeg_detected.emit)
        # Connect signal
        self.observer.schedule(event_handler, self.folder_path, recursive=False)
        self.observer.start()
        try:
            self.exec()
            # Keep the thread running
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    def stop(self):
        """Stops the observer."""
        self.observer.stop()
        self.quit()
        self.wait()

# Example: How to use this inside task_mancer_page.py
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication([])
    def on_new_jpeg_detected(file_path):
        print(f"JPEG detected: {file_path}")
        # Here you can update task_mancer_page UI with the new file
    folder_to_monitor = "D:/HL/Sc9999/Sh9992/01_BGL/01_work"
    # Update your folder path
    jpeg_monitor = JpegMonitorThread(folder_to_monitor)
    jpeg_monitor.jpeg_detected.connect(on_new_jpeg_detected)
    # Connect to UI update
    jpeg_monitor.start()
    app.exec()
