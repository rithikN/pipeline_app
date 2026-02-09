# pipeline/infra/threads/workfile_download_thread.py
from __future__ import annotations

from typing import Any, Dict, Optional, Callable

from PySide6.QtCore import Signal

from pipeline.infra.threads.base_fetch_thread import BaseFetchThread
from services.file_ops import download_task_workfile_and_deps


class WorkfileDownloadThread(BaseFetchThread):
    """
    Thread that downloads one workfile + deps.
    Emits:
      - progress(message, current, total)
      - data_fetched(summary_dict) via BaseFetchThread.safe_emit()
      - error_occurred(error_str) via BaseFetchThread.safe_error()
    """

    progress = Signal(str, int, int)

    def __init__(
        self,
        task_data: Dict[str, Any],
        file_data: Optional[Dict[str, Any]] = None,
        *,
        logger=None,
        check_ftp_connection_fn: Optional[Callable[..., bool]] = None,
    ):
        super().__init__(task_data=task_data, file_data=file_data)
        self._logger = logger
        self._check_ftp = check_ftp_connection_fn

    def run(self) -> None:
        try:
            task_data: Dict[str, Any] = self.kwargs.get("task_data") or {}
            file_data: Optional[Dict[str, Any]] = self.kwargs.get("file_data") or None

            def _progress_cb(message: str, current: int, total: int) -> None:
                self.progress.emit(message, current, total)

            summary = download_task_workfile_and_deps(
                task_data=task_data,
                file_data=file_data,
                progress_cb=_progress_cb,
                logger=self._logger,
                check_ftp_connection_fn=self._check_ftp,  # service decides if needed (is_remote_scheme)
            )

            self.safe_emit(summary.to_dict())

        except Exception as e:
            self.safe_error(e)
