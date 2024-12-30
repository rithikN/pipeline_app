from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt


class MessageBox:
    def __init__(self, parent=None):
        self.parent = parent

    def show_message(self, message, message_type="error", title="Message", rich_text=False):
        """
        Show a message using QMessageBox with different types (error, info, warning).
        :param message: The message to display in the dialog.
        :param message_type: Type of message (error, info, warning). Default is "error".
        :param title: The title of the message box (default is "Message").
        :param rich_text: Whether to render the message as rich text.
        """
        msg_box = QMessageBox(self.parent)
        msg_box.setObjectName("msg_box")

        # Set text format
        msg_box.setTextFormat(Qt.RichText if rich_text else Qt.PlainText)

        # Set icon based on message type
        if message_type == "error":
            msg_box.setIcon(QMessageBox.Critical)
        elif message_type == "info":
            msg_box.setIcon(QMessageBox.Information)
        elif message_type == "warning":
            msg_box.setIcon(QMessageBox.Warning)

        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setMinimumSize(500, 300)  # Ensure a reasonable minimum size for large messages
        msg_box.exec()

    @staticmethod
    def show_error(message, title="Error", rich_text=False):
        """Show an error message."""
        msg_box = QMessageBox()
        msg_box.setObjectName("msg_box")
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setTextFormat(Qt.RichText if rich_text else Qt.PlainText)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setMinimumSize(500, 300)
        msg_box.exec()

    @staticmethod
    def show_info(message, title="Information", rich_text=False):
        """Show an informational message."""
        msg_box = QMessageBox()
        msg_box.setObjectName("msg_box")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setTextFormat(Qt.RichText if rich_text else Qt.PlainText)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setMinimumSize(500, 300)
        msg_box.exec()

    @staticmethod
    def show_warning(message, title="Warning", rich_text=False):
        """Show a warning message."""
        msg_box = QMessageBox()
        msg_box.setObjectName("msg_box")
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setTextFormat(Qt.RichText if rich_text else Qt.PlainText)
        msg_box.setText(message)
        msg_box.setWindowTitle(title)
        msg_box.setMinimumSize(500, 300)
        msg_box.exec()


if __name__ == '__main__':
    html_message = (
        "<b>Error:</b> Missing keys in response from '<i>taskData</i>': <span style='color: red;'>task_status</span>."
        "<br><b>Received data:</b><br>"
        "<pre style='font-family: Consolas, monospace; font-size: 12px;'>"
        "[{'name': 'Test', 'status': 'in_progress', 'details': {}}]"
        "</pre>"
    )
    MessageBox.show_error(html_message, rich_text=True)
