"""
main.py

Entry point for the 3D Pipeline application. Initializes the QApplication,
applies global styles, configures logging, and runs the MainWindow.
"""

import sys
import os
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.utils.stylesheet_utils import load_stylesheet
from ui.utils.common import load_fonts_from_directory

from pipeline.config.settings import setup_logging


def main():
    """
    The main entry point for the 3D Pipeline application.
    Configures logging, loads resources, creates the QApplication,
    and starts the MainWindow.
    """
    # --- Setup logging ---
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting application...")

    # --- Create QApplication ---
    app = QApplication(sys.argv)

    # --- Load fonts ---
    fonts_dir = Path.cwd() / "resources" / "fonts"
    font_ids = load_fonts_from_directory(fonts_dir)
    if font_ids:
        logger.info("Loaded %d fonts from %s", len(font_ids), fonts_dir)
    else:
        logger.warning("No fonts loaded from %s", fonts_dir)

    # --- Set working directory (ensures resources are resolved correctly) ---
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    logger.debug("Current Working Directory: %s", os.getcwd())

    # --- Load and apply global stylesheet ---
    css_path = Path.cwd() / "ui" / "stylesheets" / "app_style.css"
    load_stylesheet(app, css_path)

    # --- Launch Main Window ---
    window = MainWindow()
    window.show()

    logger.info("Application initialized. Entering main event loop.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
