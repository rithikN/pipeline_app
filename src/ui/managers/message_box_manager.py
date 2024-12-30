from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication
from ui.components.extensions.message_box import MessageBox


class MessageBoxManager:
    """
    Centralized manager for displaying QMessageBoxes in a thread-safe manner.
    Utilizes QTimer.singleShot to ensure MessageBox operations occur on the main thread.
    """

    @staticmethod
    def show_error(message, title="Error", rich_text=False):
        """
        Show an error message in a thread-safe manner.
        :param message: The message to display.
        :param title: The title of the error dialog.
        :param rich_text: Whether to render the message as rich text.
        """
        app = QApplication.instance()
        if app:
            QTimer.singleShot(
                0, lambda: MessageBox.show_error(message, title=title, rich_text=rich_text)
            )
        else:
            print(f"{title}: {message}")

    @staticmethod
    def show_info(message, title="Information", rich_text=False):
        """
        Show an informational message in a thread-safe manner.
        :param message: The message to display.
        :param title: The title of the information dialog.
        :param rich_text: Whether to render the message as rich text.
        """
        app = QApplication.instance()
        if app:
            QTimer.singleShot(
                0, lambda: MessageBox.show_info(message, title=title, rich_text=rich_text)
            )
        else:
            print(f"{title}: {message}")

    @staticmethod
    def show_warning(message, title="Warning", rich_text=False):
        """
        Show a warning message in a thread-safe manner.
        :param message: The message to display.
        :param title: The title of the warning dialog.
        :param rich_text: Whether to render the message as rich text.
        """
        app = QApplication.instance()
        if app:
            QTimer.singleShot(
                0, lambda: MessageBox.show_warning(message, title=title, rich_text=rich_text)
            )
        else:
            print(f"{title}: {message}")
