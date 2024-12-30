from PySide6.QtWidgets import QComboBox, QApplication, QListView
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, Signal


class MultiSelectComboBox(QComboBox):
    selectionChanged = Signal(list)  # Signal to emit when selection changes
    currentTextChanged = Signal(str)  # Signal to emit when the displayed text changes

    def __init__(self, placeholder, parent=None):
        super().__init__(parent)
        self.setView(QListView())
        self.setModel(QStandardItemModel(self))
        self._selected_items = []
        self._is_updating = False
        self.placeholder = placeholder
        self._first_item_added = False

        # Handle combo box activation
        self.view().pressed.connect(self.handle_item_pressed)

        # Set placeholder text
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setPlaceholderText(self.placeholder)

        # Remove the dropdown arrow
        self.setStyleSheet("QComboBox::drop-down { border: 0px; }")
        # Resize the lineEdit for better display
        self.lineEdit().setAlignment(Qt.AlignLeft)
        self.lineEdit().setContentsMargins(5, 0, 5, 0)

        # Style
        self.setStyleSheet("""
            QComboBox {
                background-color: #E1E1E8;
                color: #000000;
                border: 2px solid #000000;
                border-radius: 5px;
                padding: 5px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
                background: transparent;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url("resources/icons/down-arrow.png");  /* Default Qt arrow icon */
                width: 15px;
                height: 15px;
            }
            QComboBox QAbstractItemView {
                background-color: #E1E1E8;
                color: #000000;
                selection-background-color: #1e90ff;
                selection-color: #E1E1E8;
                padding: 5px;
                border: 1px solid #cccccc;
            }
            QAbstractItemView::item {
                padding: 8px;
                margin: 3px 5px;
                border-radius: 5px;
            }
            QAbstractItemView::item:hover {
                background-color: #3b5998;
            }
            QAbstractItemView::item:selected {
                background-color: #000000;
                color: #1e90ff;
            }
        """)

        # Connect signals
        self.currentIndexChanged.connect(self.handle_index_changed)

    def handle_index_changed(self, index):
        """Handle index changes and check if the first item is selected."""
        if index == 0:  # Check if the first item is selected
            self.deselect_all()
            # Update placeholder text
            self.lineEdit().setText(self.placeholder)
            self.selectionChanged.emit([])  # Emit signal with empty selection

    def deselect_all(self):
        """Deselect all items."""
        for row in range(self.model().rowCount()):
            item = self.model().item(row)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Unchecked)
        self._selected_items = []

    def addItem(self, text, data=None):
        """Add a single item with or without a checkbox."""
        item = QStandardItem(text)
        if not self._first_item_added:
            # First item: No checkbox
            item.setFlags(Qt.ItemIsEnabled)
            self._first_item_added = True
        else:
            # Subsequent items: Add checkbox
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
            item.setData(Qt.Unchecked, Qt.CheckStateRole)
        item.setData(data, Qt.UserRole)
        self.model().appendRow(item)

    def addItems(self, texts):
        """Add multiple items with checkboxes (except for the first item)."""
        for text in texts:
            self.addItem(text)

    def handle_item_pressed(self, index):
        """Handle item press events with special behavior for the first item."""
        if self._is_updating:
            return

        item = self.model().itemFromIndex(index)

        if index.row() == 0:  # First element pressed
            # Deselect all other items
            self.deselect_all()
            # Update display to show only the placeholder text
            self.lineEdit().setText(self.placeholder)

            # Emit signal with an empty list, as nothing is selected
            self.selectionChanged.emit([])
        else:
            # Deselect the first item if any other item is selected
            first_item = self.model().item(0)
            if first_item:
                first_item.setCheckState(Qt.Unchecked)

            # Toggle the current item's state
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)

        self.update_selected_items()

    def update_selected_items(self):
        """Update the list of selected items and display them."""
        self._is_updating = True
        self._selected_items = []
        selected_texts = []

        for row in range(self.model().rowCount()):
            item = self.model().item(row)
            if item.flags() & Qt.ItemIsUserCheckable and item.checkState() == Qt.Checked:
                self._selected_items.append(item)
                selected_texts.append(item.text())

        # Update the placeholder text or display selected items
        display_text = ", ".join(selected_texts) if selected_texts else self.placeholder
        self.lineEdit().setText(display_text)

        # Emit signals
        self.selectionChanged.emit(selected_texts)
        self.currentTextChanged.emit(display_text)  # Emit the currentTextChanged signal

        self._is_updating = False

    def selectedItems(self):
        """Return a list of selected items' texts."""
        return [item.text() for item in self._selected_items]

    def setSelectedItems(self, texts):
        """Set the selected items programmatically."""
        self._is_updating = True
        for row in range(self.model().rowCount()):
            item = self.model().item(row)
            if item.text() in texts and (item.flags() & Qt.ItemIsUserCheckable):
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
        self.update_selected_items()
        self._is_updating = False


# Example usage
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    combo = MultiSelectComboBox("Scene")
    combo.addItems([
        "Select All", "sc0000", "sc0010", "sc0020", "sc0490",
        "sc0865", "sc0950", "sc1451", "sc4650",
        "sc9998", "sc9999"
    ])
    combo.resize(200, 30)
    combo.show()


    def on_selection_changed(selected):
        print("Selected items:", selected)


    def on_text_changed(text):
        print("Current text changed:", text)


    combo.selectionChanged.connect(on_selection_changed)
    combo.currentTextChanged.connect(on_text_changed)

    sys.exit(app.exec())
