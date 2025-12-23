"""
asset_list.py

Provides the Asset List Floating Window class, which displays a list of assets
for a selected task, with various actions to download or update the asset files
and open the asset directory.
"""

import os
import logging
from typing import Dict, List
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QSizePolicy, QFrame
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QIcon, QCursor

from ui.components.extensions.message_box import MessageBox

logger = logging.getLogger(__name__)


def _warning_button_style() -> str:
    return """
        QPushButton {
            background-color: #d7455f;
        }
        QPushButton:hover {
            background-color: #e2919f;
        }
        QPushButton:pressed {
            background-color: #821729;
        }
    """


def _open_button_style() -> str:
    return """
        QPushButton {
            background-color: #c7b299;
        }
        QPushButton:hover {
            background-color: #a68154;
        }
        QPushButton:pressed {
            background-color: #503514;
        }
    """


class AssetRow(QWidget):
    """
    Widget representing a single asset row with corresponding actions.
    """

    assetSelected = Signal(str, dict)
    openRequested = Signal(dict)
    warningRequested = Signal(dict)
    missingRequested = Signal(dict)

    def __init__(self, asset_name: str, asset_dict: dict, thumbnail_path: str = "thumbnail.webp"):
        """
        Create row for Asset.
        Args:
            asset_name (string)
        """
        super().__init__()
        logger.debug(f"Creating row for asset: {asset_name}")

        self.asset_name = asset_name
        self.asset = asset_dict
        self.message_box = MessageBox()

        self.setFixedHeight(50)

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # Asset name label
        label = QLabel(asset_name)
        label.setStyleSheet("color: #E1E1E8;")
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(label)

        # Action buttons based on asset status
        if asset_dict.get("is_server_file"):
            if not asset_dict.get("is_updated"):
                warning_btn = QPushButton()
                warning_btn.setToolTip("Asset file is not up to date.")
                warning_btn.setIcon(QIcon("resources/icons/menu_bar/warning.svg"))
                warning_btn.setCursor(QCursor(Qt.PointingHandCursor))
                warning_btn.setStyleSheet(_warning_button_style())
                warning_btn.clicked.connect(lambda: self.warningRequested.emit(self.asset))
                layout.addWidget(warning_btn)

            open_btn = QPushButton()
            open_btn.setToolTip("Open asset directory.")
            open_btn.setIcon(QIcon("resources/icons/detail_form/explorer.svg"))
            open_btn.setCursor(QCursor(Qt.PointingHandCursor))
            open_btn.setStyleSheet(_open_button_style())
            open_btn.clicked.connect(lambda: self.openRequested.emit(self.asset))
            layout.addWidget(open_btn)
        else:
            missing_btn = QPushButton()
            missing_btn.setToolTip("Missing asset.")
            missing_btn.setIcon(QIcon("resources/icons/menu_bar/exit.svg"))
            missing_btn.setCursor(QCursor(Qt.PointingHandCursor))
            missing_btn.setStyleSheet(_warning_button_style())
            missing_btn.clicked.connect(lambda: self.missingRequested.emit(self.asset))
            layout.addWidget(missing_btn)

        self.setLayout(layout)


class GroupHeader(QLabel):
    """Styled group header for asset categories."""

    def __init__(self, group_name: str):
        super().__init__(group_name)
        self.setStyleSheet(
            "color: #E1E1E8; font-size: 14px; font-weight: bold; "
            "padding-top: 30px; padding-bottom: 15px;"
        )


class AssetListDialog(QDialog):
    """
    Floating window displaying a list of assets for a selected task.
    """

    assetSelected = Signal(str, dict)

    def __init__(self, task_name: str, assets: List[Dict]):
        """
        Initialize the AssetListWidget.
        """
        super().__init__()
        logger.debug("Initializing AssetListDialog.")

        self.setWindowTitle(f"Asset List: {task_name}")
        self.setMinimumSize(QSize(650, 500))
        self.setMaximumHeight(500)
        self.setSizeGripEnabled(True)
        self.setWindowFlags(self.windowFlags() | Qt.Window)

        asset_list_layout = QVBoxLayout(self)

        # Scroll Area Setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(0)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        group_order = ["Characters", "Props", "Locations"]
        grouped_assets = {group: [] for group in group_order}

        for asset in assets:
            grouped_assets.get(asset.get("group"), []).append(asset.get("name"))

        for group in group_order:
            names = sorted(grouped_assets.get(group, []))
            if not names:
                continue

            scroll_layout.addWidget(GroupHeader(group))

            group_sep = QFrame()
            group_sep.setFrameShape(QFrame.HLine)
            group_sep.setStyleSheet("color: #E1E1E8;")
            group_sep.setFixedHeight(2)
            scroll_layout.addWidget(group_sep)

            for asset_name in names:
                asset_dict = next((item for item in assets if item.get("name") == asset_name), None)
                if asset_dict:
                    scroll_layout.addWidget(AssetRow(asset_name, asset_dict))

                    row_separator = QFrame()
                    row_separator.setFrameShape(QFrame.HLine)
                    row_separator.setStyleSheet("color: #252B36;")
                    row_separator.setFixedHeight(1)
                    scroll_layout.addWidget(row_separator)

        scroll_area.setWidget(scroll_content)
        asset_list_layout.addWidget(scroll_area)

        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        asset_list_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignCenter)


# Example usage
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)

    example_assets = [
        {"name": "HeroCharacter", "group": "Characters", "is_server_file": True, "is_updated": False, "path": "Hero"},
        {"name": "Sword", "group": "Props", "is_server_file": True, "is_updated": True, "path": "Sword"},
        {"name": "Castle", "group": "Locations", "is_server_file": False, "is_updated": False, "path": "Castle"},
    ]

    dialog = AssetListDialog(task_name="TestTask", assets=example_assets)
    dialog.exec()
