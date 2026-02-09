# controllers/task_controller.py

import os, subprocess
from pathlib import Path
import logging
from typing import Optional, Dict, Any

from controllers.base_controller import BaseController
from services.data_service import check_ftp_connection

# ToD deprecate domain services
from pipeline.domain.services import task_service
from pipeline.infra.rclone import copy_through_rclone
from pipeline.infra.kitsu_client import fetch_data_from_kitsu
from pipeline.domain.services.asset_mapping import resolve_asset_info
from pipeline.domain.services.assets import get_local_asset_base
from pipeline.config.settings import ASSET_SERVER_BASE

from pipeline.events import Event
from services import wfh_mapping  # you already have this
from pipeline.infra.threads.workfile_download_thread import WorkfileDownloadThread

logger = logging.getLogger(__name__)


class TaskController(BaseController):
    """
    Orchestrates operations related to tasks:
    - Download task files (legacy)
    - Download selected workfile + dependencies (new)
    - Upload input files
    - Track assets
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._active_threads = set()  # keep QThreads alive

    # --------------------
    # Download (Legacy + New)
    # --------------------
    def handle_download(self, task_data: dict):
        title = "Download"
        message = f"Downloading {task_data.get('name')}"
        payload = {"task": task_data}

        # Start progress (manual, async-safe)
        if self.event_manager and not self.headless:
            self.event_manager.progressStarted.emit(
                Event(type="progress", title=title, message=message, payload=payload))
        else:
            logger.info(f"[START] {title}: {message}")

        th = WorkfileDownloadThread(
            task_data=task_data,
            logger=logger,
            check_ftp_connection_fn=check_ftp_connection,  # service must call only when is_remote_scheme(src)
        )

        # keep thread alive using existing BaseController tracking
        self.add_worker(th)

        def _finish_ok(summary: dict):
            # remove first
            self.remove_worker(th)

            # close progress dialog
            if self.event_manager and not self.headless:
                self.event_manager.progressFinished.emit(
                    Event(type="success", title=title, message="Download completed",
                          payload={"task": task_data, "summary": summary})
                )
            else:
                logger.info(f"[SUCCESS] {title}")

            # optional: also publish a richer event if your UI listens for it
            self.publish_event(
                "workfileDownloadFinished",
                Event(type="success", title=title, message="Download completed",
                      payload={"task": task_data, "summary": summary}),
            )

        def _finish_err(err: str):
            self.remove_worker(th)

            if self.event_manager and not self.headless:
                self.event_manager.errorOccurred.emit(
                    Event(type="error", title=title, message=str(err), payload={"task": task_data})
                )
            else:
                logger.error(f"[ERROR] {title}: {err}")

            self.publish_event(
                "workfileDownloadError",
                Event(type="error", title="Download error", message=str(err), payload={"task": task_data}),
            )

        th.progress.connect(
            lambda m, c, t: self.publish_event(
                "workfileDownloadProgress",
                Event(type="progress", title=title, message=f"{m} ({c}/{t})", payload={"task": task_data}),
            )
        )
        th.data_fetched.connect(_finish_ok)
        th.error_occurred.connect(_finish_err)

        th.start()

    # --------------------
    # Upload
    # --------------------
    def handle_upload(self, task_data: dict):
        with self.operation(
            title="Upload Task",
            message=f"Uploading input files for {task_data['name']}",
            payload=task_data,
        ):
            if not check_ftp_connection(check_FTP_conn=True):
                raise RuntimeError("FTP connection failed")

            local_input = Path(task_data.get("input_directory"))
            ftp_input = task_data.get("ftp_input_directory")

            if local_input.exists():
                status = copy_through_rclone(
                    "copy", local_input.as_posix(), ftp_input, flags=["--update"]
                )
                if status != 0:
                    raise RuntimeError("Upload failed")

    # --------------------
    # Asset Tracker
    # --------------------
    def handle_asset_tracker(self, task_data: dict):
        """
        Fetch assets from Kitsu, sync locally, then notify UI via events.
        """
        with self.operation(
                title="Asset Tracker",
                message=f"Fetching assets for {task_data['name']}",
                payload=task_data,
        ):
            try:
                project, sequence, shot = task_data["name"].split("_")[0:3]
                kitsu_data = {"project": project, "sequence": sequence, "shot": shot}
                kitsu_resp = fetch_data_from_kitsu(kitsu_data)

                raw_assets = kitsu_resp.get("data", {}).get("shot_breakdown", []) or []
                if not raw_assets:
                    self.publish_event(
                        "assetTrackerEmpty",
                        Event(
                            type="warning",
                            title="Asset Tracker",
                            message="No assets assigned to this shot.",
                            payload={"task": task_data},
                        ),
                    )
                    return []

                server_base = ASSET_SERVER_BASE
                local_base = get_local_asset_base(project)

                asset_list = []
                for asset in raw_assets:
                    group, asset_dir = resolve_asset_info(asset)
                    rel_path = f"{asset_dir}/{asset['asset_name']}"
                    remote = f"{server_base}/{rel_path}"
                    local = (local_base / rel_path).as_posix()

                    entry = {
                        "name": asset["asset_name"],
                        "group": group,
                        "path": rel_path,
                        "is_server_file": False,
                        "is_updated": False,
                    }

                    if copy_through_rclone("lsd", src=remote) == 0:
                        entry["is_server_file"] = True
                        up_to_date = copy_through_rclone(
                            "check", src=remote, dest=local, flags=["--update", "--quiet"]
                        )
                        if up_to_date == 0:
                            entry["is_updated"] = True
                        else:
                            status = copy_through_rclone(
                                "sync", src=remote, dest=local, flags=["--update"]
                            )
                            if status == 0:
                                entry["is_updated"] = True

                    asset_list.append(entry)

                # Publish success event
                self.publish_event(
                    "assetListReady",
                    Event(
                        type="success",
                        title="Asset Tracker",
                        message=f"Fetched {len(asset_list)} assets for {task_data['name']}",
                        payload={"task": task_data, "assets": asset_list},
                    ),
                )

                return asset_list

            except Exception as e:
                logger.error(f"Asset tracker failed: {e}", exc_info=True)
                self.publish_event(
                    "assetTrackerError",
                    Event(
                        type="error",
                        title="Asset Tracker Error",
                        message=f"Failed to fetch assets: {e}",
                        payload={"task": task_data},
                    ),
                )
                return []

    def handle_open_asset(self, asset: dict):
        """
        Open asset directory in file explorer.
        """
        with self.operation(
            title="Open Asset Folder",
            message=f"Opening asset folder for {asset.get('name')}",
            payload=asset,
        ):
            asset_dir = asset.get("path")
            try:
                if os.name == "nt":  # Windows
                    local_dir = Path("D:/Heirloom/Heirloom_Project/Assets")
                    os.startfile(local_dir / asset_dir)
                else:  # macOS/Linux
                    local_dir = Path.home() / "Documents" / "Heirloom" / "Heirloom_Project" / "Assets"
                    subprocess.run(["open", str(local_dir / asset_dir)], check=True)

                # ToDo optional: publish success event
                # self.publish_event(
                #     "assetOpened",
                #     Event(
                #         type="success",
                #         title="Open Asset Folder",
                #         message=f"Opened folder for {asset.get('name')}",
                #         payload=asset,
                #     ),
                # )

            except Exception as e:
                logger.error(f"Failed to open asset {asset.get('name')}: {e}", exc_info=True)
                raise RuntimeError(f"Could not open explorer for {asset.get('name')}: {e}")

    def handle_missing_asset(self, asset: dict):
        """
        Handle missing asset by publishing a structured event.
        """
        with self.operation(
                title="Missing Asset",
                message=f"Asset {asset.get('name')} not found on server",
                payload=asset,
        ):
            logger.warning(f"Asset missing: {asset.get('name')}")

            # ToDo optional: publish missing event
            # self.publish_event(
            #     "assetMissing",
            #     Event(
            #         type="error",
            #         title="Asset Missing",
            #         message=f"{asset.get('name')} is not available on the server.\nPlease contact the Production team.",
            #         payload=asset,
            #     ),
            # )

    def handle_asset_warning(self, asset: dict):
        """
        Handle outdated asset by publishing a structured event.
        """
        with self.operation(
                title="Outdated Asset",
                message=f"Asset {asset.get('name')} is outdated",
                payload=asset,
        ):
            logger.warning(f"Asset not up to date: {asset.get('name')}")

            # ToDo optional: publish warning event
            # self.publish_event(
            #     "assetOutdated",
            #     Event(
            #         type="warning",
            #         title="Asset Not Updated",
            #         message=f"{asset.get('name')} is not up to date.\n"
            #                 f"Please download the latest asset file or contact the Production team.",
            #         payload=asset,
            #     ),
            # )

