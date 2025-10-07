
from PySide6.QtCore import QThread, Signal, QTimer
import logging

from services.data_service import (get_taskData, get_taskStatus)

# Initialize logger
logger = logging.getLogger(__name__)

class DataFetchThread(QThread):
    """
    Thread responsible for fetching data related to tasks and their statuses.
    Emit signals on success or error.
    """
    data_fetched   = Signal(list, dict)
    error_occurred = Signal(str)

    def __init__(self, project_data):
        """
        Initialize the DataFetchThread.

        Args:
            project_data (dict): Dictionary containing project-related information (e.g., project name).
        """
        super().__init__()
        self.project_data = project_data

    # def run(self):
    #     """
    #     Fetch task data and task status in a background thread. Emit signals upon completion or error.
    #     """
    #     logger.debug("DataFetchThread started. Fetching task data and task status.")
    #     try:
    #         task_data = get_taskData(self.project_data)
    #         if not task_data:
    #             raise Exception("Failed to fetch task data.")
    #         # task_status = get_taskStatus(self.project_data)
    #         task_status = get_taskStatus(task_data)
    #         if not task_status:
    #             raise Exception("Failed to fetch task status.")
    #         logger.debug("Data fetched successfully, emitting data_fetched signal.")
    #         self.data_fetched.emit(task_data, task_status)
    #     except Exception as e:
    #         logger.error(f"Error in DataFetchThread: {e}", exc_info=True)
    #         self.error_occurred.emit(str(e))

    def run(self):
        """
        Fetch task data and task status in a background thread. Emit signals upon completion or error.
        """
        logger.debug(f"DataFetchThread started. Fetching task data and task status. {self.project_data}")
        try:
            print("Fetching task data and task status", self.project_data)
            task_data = get_taskData(self.project_data)
            if not task_data:
                # print("line 55")s
                # raise Exception("Failed to fetch Task Data.")
                raise Exception("Currently no Task assigned to you !\nKindly contact the Production Team.")
            # task_status = get_taskStatus(self.project_data)
            task_status = get_taskStatus(task_data)
            if not task_status:
                # print("line 60")
                raise Exception("Failed to fetch Task Status.")
            logger.debug("Data fetched successfully, emitting data_fetched signal.")
            self.data_fetched.emit(task_data, task_status)
        except Exception as e:
            logger.error(f"Error in DataFetchThread: {e}", exc_info=True)
            self.error_occurred.emit(str(e)) 