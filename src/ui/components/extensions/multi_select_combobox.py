from PySide6.QtWidgets import QComboBox, QListView, QLineEdit, QApplication
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, Signal, QEvent


class MultiSelectComboBox(QComboBox):
    selectionChanged = Signal(list)
    currentTextChanged = Signal(str)

    def __init__(self, placeholder, parent=None):
        super().__init__(parent)
        self.setView(QListView())
        self.setModel(QStandardItemModel(self))
        self._selected_items = []
        self._is_updating = False
        self.placeholder = placeholder
        self._first_item_added = False

        # Setup combo as editable with a read-only line edit
        self.setEditable(True)
        line_edit = self.lineEdit()
        line_edit.setReadOnly(True)
        line_edit.setPlaceholderText(self.placeholder)
        line_edit.setAlignment(Qt.AlignLeft)

        # --- Install event filter on the line edit ---
        line_edit.installEventFilter(self)

        self.view().pressed.connect(self.handle_item_pressed)
        self.currentIndexChanged.connect(self.handle_index_changed)

    def eventFilter(self, obj, event):
        """
        Capture mouse presses on the line edit, and open/close the popup
        so that clicking *anywhere* in the combobox triggers the dropdown.
        """
        if obj == self.lineEdit() and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                if self.view().isVisible():
                    self.hidePopup()
                else:
                    self.showPopup()
            return True
        return super().eventFilter(obj, event)

    def handle_index_changed(self, index):
        if index == 0:
            self.deselect_all()
            self.lineEdit().setText(self.placeholder)
            self.selectionChanged.emit([])

    def deselect_all(self):
        for row in range(self.model().rowCount()):
            item = self.model().item(row)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Unchecked)
        self._selected_items = []

    def addItem(self, text, data=None):
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
        for text in texts:
            self.addItem(text)

    def handle_item_pressed(self, index):
        if self._is_updating:
            return
        item = self.model().itemFromIndex(index)

        if index.row() == 0:
            # "Select All" / first element pressed => deselect everything
            self.deselect_all()
            self.lineEdit().setText(self.placeholder)
            self.selectionChanged.emit([])
        else:
            # Deselect the first item if any other item is selected
            first_item = self.model().item(0)
            if first_item:
                first_item.setCheckState(Qt.Unchecked)

            # Toggle check state
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)

        self.update_selected_items()

    def update_selected_items(self):
        self._is_updating = True
        self._selected_items = []
        selected_texts = []

        for row in range(self.model().rowCount()):
            item = self.model().item(row)
            if item.flags() & Qt.ItemIsUserCheckable and item.checkState() == Qt.Checked:
                self._selected_items.append(item)
                selected_texts.append(item.text())

        display_text = ", ".join(selected_texts) if selected_texts else self.placeholder
        self.lineEdit().setText(display_text)

        self.selectionChanged.emit(selected_texts)
        self.currentTextChanged.emit(display_text)

        self._is_updating = False

    def selectedItems(self):
        return [item.text() for item in self._selected_items]

    def setSelectedItems(self, texts):
        self._is_updating = True
        for row in range(self.model().rowCount()):
            item = self.model().item(row)
            if item.text() in texts and (item.flags() & Qt.ItemIsUserCheckable):
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
        self.update_selected_items()
        self._is_updating = False


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
