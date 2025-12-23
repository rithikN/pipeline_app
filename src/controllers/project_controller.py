import os
import logging
from pathlib import Path

from controllers.base_controller import BaseController
from pipeline.config.settings import SYSTEM
from pipeline.infra.rclone import copy_through_rclone
from pipeline.events import Event

logger = logging.getLogger(__name__)


class ProjectController(BaseController):
    """
    Handles project-wide operations (sync, downloading project files, etc.).
    """

    def handle_download_project_files(self, project_data: dict):
        """
        Download global project files (scripts, tech docs, references, etc.)
        from the server to the local workspace.
        """
        with self.operation(
            title="Download Project Files",
            message="Downloading project-wide files...",
            payload=project_data,
        ):
            dir_list = [
                "01_Script", "01_Tech Documents", "02_Bibles",
                "11_Benchmark", "09_Brief & References", "12_Color Script"
            ]

            # ToDo Logic should be in config
            server_base_path = Path("hlm:/Heirloom_Server/Assets")
            if SYSTEM == "Windows":
                local_base_path = Path("D:/Heirloom/Heirloom_Project/Assets")
            elif SYSTEM == "Darwin":
                local_base_path = Path.home() / "Documents" / "Heirloom" / "Heirloom_Project" / "Assets"
            else:
                raise RuntimeError(f"Unsupported system: {SYSTEM}")

            failed = []

            for file_dir in dir_list:
                server_asset_path = server_base_path / file_dir
                local_asset_path = local_base_path / file_dir

                os.makedirs(local_asset_path, exist_ok=True)

                if copy_through_rclone("lsd", src=server_asset_path) == 0:
                    status = copy_through_rclone(
                        "sync",
                        src=server_asset_path,
                        dest=local_asset_path,
                        flags=["--update"]
                    )
                    if status != 0:
                        failed.append(str(server_asset_path))
                else:
                    failed.append(str(server_asset_path))

            if failed:
                msg = f"Some project files failed to download: {failed}"
                logger.error(msg)
                raise RuntimeError(msg)

            # Publish success event
            self.publish_event(
                "projectSynced",
                Event(
                    type="success",
                    title="Project Sync",
                    message="Project files downloaded successfully.",
                    payload={"project": project_data, "local_base": str(local_base_path)},
                ),
            )
