from PySide6.QtWidgets import QApplication, QDialog, QListWidget, QVBoxLayout, QPushButton
import sys


class ItemSelectionDialog(QDialog):
    def __init__(self, items, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Item")
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.addItems(items)
        layout.addWidget(self.list_widget)

        select_button = QPushButton("Select")
        select_button.clicked.connect(self.accept)
        layout.addWidget(select_button)

        self.setLayout(layout)

    def get_selected_item(self):
        return self.list_widget.currentItem().text() if self.list_widget.currentItem() else None


def handle_Selector():
    """
    Handle the 'Create File' button click. This function will
    open a modal dialog, get the selected item, and call the backend API.
    """
    print("Create File button clicked.")

    items = ["Option 1", "Option 2", "Option 3"]  # Example items
    dialog = ItemSelectionDialog(items)

    if dialog.exec():
        selected_item = dialog.get_selected_item()
        if selected_item:
            print(f"File created with item: {selected_item}")
        else:
            print("No item selected")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    handle_Selector()
    sys.exit(app.exec())
