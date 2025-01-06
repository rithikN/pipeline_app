"""
main.py

Entry point for the 3D Pipeline application. Initializes the QApplication,
applies global styles, configures logging, and runs the MainWindow.
"""

import sys
import os
import logging
from logging.handlers import RotatingFileHandler

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont

from ui.main_window import MainWindow
from ui.utils.stylesheet_loader import load_stylesheet
from ui.utils.common import load_fonts_from_directory


def setup_logging():
    """
    Configure the logging system for the entire application.
    This sets up both console logging and a rotating file handler.
    """
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.CRITICAL)

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Rotating file handler (logs up to 5 MB, keeps 3 backups)
    file_handler = RotatingFileHandler('app.log', maxBytes=5_000_000, backupCount=3)
    file_handler.setLevel(logging.INFO)

    # Create formatters and add them to handlers
    console_format = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    file_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(funcName)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logging.info("Logging is set up.")


def main():
    """
    The main entry point for the 3D Pipeline application. Configures logging,
    creates the QApplication, applies a global stylesheet, and shows the MainWindow.
    """
    # Set up logging for the application
    setup_logging()

    logging.info("Starting application...")

    # Create the QApplication
    app = QApplication(sys.argv)

    font_id_arimo = QFontDatabase.addApplicationFont("resources/fonts/Arimo/Arimo-VariableFont_wght.ttf")
    font_id_inter = QFontDatabase.addApplicationFont("resources/fonts/Inter/Inter-VariableFont_opsz,wght.ttf")

    if font_id_arimo == -1 or font_id_inter == -1:
        logging.debug("Failed to load fonts.")
    else:
        logging.debug("Loaded arimo and inter fonts ")

    # Change to the directory of this file (ensures resources are found correctly)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    logging.debug(f"Current Working Directory: {os.getcwd()}")

    # Load and apply the global app stylesheet
    load_stylesheet(app, "ui/stylesheets/app_style.css")

    # Initialize and run MainWindow
    window = MainWindow()
    window.show()

    logging.info("Application initialized. Entering main event loop.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
