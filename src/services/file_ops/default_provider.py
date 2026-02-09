# data_service/file_ops/default_provider.py
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from services.constants import EXCLUDE_MAC_FILES

from .task_context import TaskContext
from .mapping import PathMapper, UNCResolver
from .wfh import WFHMappingService, WFHWorkfileVisibilityPolicy, resolve_unc_root
from .workfiles import WorkfileScanner
from .versioning import find_latest_version_on_disk
from .downloader import DownloadTaskUseCase
from .transport.copy_service import CopyService, CopyPolicy
from .transport.rclone_transport import RcloneTransport
from .transport.shutil_transport import ShutilTransport
from .rclone_flags import default_rclone_flags, sanitize_rclone_flags_for_copyto
from .udim import UdimCopyService
from .bfs_maya import MayaDepsBFSService, DefaultMayaDepsGateway

logger = logging.getLogger(__name__)

class DefaultFileOpsProvider:
    def __init__(self):
        # build services once (composition root)
        self._wfh_mapping = WFHMappingService(logger=logger)

        self._scanner = WorkfileScanner(
            exclude_mac_files=set(EXCLUDE_MAC_FILES),
        )

    def filter_workfiles_for_wfh(self, task_data: dict, work_files: list[dict]) -> list[dict]:
        ctx = TaskContext.from_task(task_data)
        unc_root = resolve_unc_root(task_data)  # reads env PIPELINE_SERVER_UNC_ROOT / {SHOW}_SERVER_UNC_ROOT
        policy = WFHWorkfileVisibilityPolicy(
            mapping_service=self._wfh_mapping,
            unc_resolver=UNCResolver(unc_root=unc_root),
            logger=logger,
        )
        return policy.apply(task_data, work_files)

    def get_work_files(self, task_data: dict) -> list[dict]:
        ctx = TaskContext.from_task(task_data)
        if ctx.is_remote:
            self._wfh_mapping.ensure_z_mapped(task_data)

        results = self._scanner.scan_work_dir(task_data)
        return self.filter_workfiles_for_wfh(task_data, results)

    def sync_local_files(self, task: dict) -> list[dict]:
        wf = (task or {}).get("work_files")
        if isinstance(wf, list) and wf:
            return wf
        return self.get_work_files(task)

    def find_latest_version_on_disk(self, file_path: str):
        return find_latest_version_on_disk(file_path)

    def download_task_workfile_and_deps(self, task_data: Dict[str, Any], file_data: Optional[Dict[str, Any]] = None, **kwargs):
        ctx = TaskContext.from_task(task_data)

        # transports + copy service
        flags = default_rclone_flags()
        rclone = RcloneTransport(flags=flags, sanitize_for_copyto_fn=sanitize_rclone_flags_for_copyto)
        shutil_t = ShutilTransport(logger=kwargs.get("logger"))

        copy = CopyService(
            rclone=rclone,
            shutil=shutil_t,
            policy=CopyPolicy(prefer_rclone=ctx.prefer_rclone),
            logger=kwargs.get("logger"),
        )

        udim = UdimCopyService(copy_service=copy, logger=kwargs.get("logger"))

        bfs = MayaDepsBFSService(
            deps_gateway=DefaultMayaDepsGateway(),
            copy_service=copy,
            udim_service=udim,
            logger=kwargs.get("logger"),
        )

        usecase = DownloadTaskUseCase(
            wfh_mapping=self._wfh_mapping,
            mapper=PathMapper(ctx.path_map),
            copy_service=copy,
            udim_service=udim,
            bfs_service=bfs,
            logger=kwargs.get("logger"),
        )
        return usecase.run(task_data=task_data, file_data=file_data, **kwargs)
