# pipeline/infra/threads/project_fetch_thread.py
import logging
from services.data_service import get_taskData, get_taskStatus
from .base_fetch_thread import BaseFetchThread

logger = logging.getLogger(__name__)


class ProjectDataFetchThread(BaseFetchThread):
    """
    Fetches task data + task statuses for a given project.
    """

    def run(self):
        try:
            project_data = self.kwargs.get("project_data")
            logger.debug("ProjectDataFetchThread started with %s", project_data)

            task_data = get_taskData(project_data)
            if not task_data:
                raise Exception("Currently no tasks assigned. Contact Production Team.")

            task_status = get_taskStatus(task_data)
            if not task_status:
                raise Exception("Failed to fetch task statuses.")

            self.safe_emit((task_data, task_status))

        except Exception as e:
            self.safe_error(e)
