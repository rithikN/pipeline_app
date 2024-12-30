from services.constants import TASK_NAME, TASK_STATUS


class TaskFilter:
    def __init__(self, tasks):
        """
        Initialize the TaskFilter with a list of tasks.
        :param tasks: List of task dictionaries.
        """
        self.original_tasks = tasks

    def filter(self, search_text="", selection=None):
        """
        Filters the tasks based on search text and selection filters.
        :param search_text: A comma-separated string for search criteria.
        :param selection: A dictionary of selection filters.
        :return: List of filtered tasks.
        """
        search_criteria = self._parse_search_criteria(search_text)
        return [
            task for task in self.original_tasks
            if self._matches_search_criteria(task, search_criteria)
               and self._matches_selection(task, selection)
        ]

    def _parse_search_criteria(self, search_text):
        """Splits search text into a list of lowercase criteria."""
        return [criterion.strip().lower() for criterion in search_text.split(",") if criterion.strip()]

    def _matches_search_criteria(self, task, search_criteria):
        """Checks if a task matches any of the search criteria."""
        if not search_criteria:  # No search criteria means no filtering
            return True
        return any(criterion in task[TASK_NAME].lower() for criterion in search_criteria)

    def _matches_selection(self, task, selection):
        """Checks if a task matches all active selection filters."""
        if not selection:  # No selection filters mean no filtering
            return True

        def matches_filter(value, filter_values):
            """Case-insensitive matching for a task value and filter values."""
            if not filter_values:
                return True
            if not isinstance(filter_values, list):
                filter_values = [filter_values]
            return any(fv.lower() in value.lower() for fv in filter_values)

        return (
                matches_filter(task[TASK_NAME], selection.get("task")) and
                matches_filter(task[TASK_NAME], selection.get("episode")) and
                matches_filter(task[TASK_NAME], selection.get("scene")) and
                matches_filter(task[TASK_STATUS], selection.get("status"))
        )


if __name__ == '__main__':
    tasks = [
        {"task_name": "Animate Scene 1", "task_status": "Approved"},
        {"task_name": "Lighting Scene 2", "task_status": "Pending"},
        {"task_name": "Layout Scene 1", "task_status": "Completed"}
    ]

    selection = {"task": ["animate", "layout"], "status": ["approved"]}
    search_text = "scene 1"

    task_filter = TaskFilter(tasks)
    filtered = task_filter.filter(search_text, selection)
    print(filtered)
