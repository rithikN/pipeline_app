import os
import re

from pathlib import Path
from datetime import datetime
import logging
from pprint import pprint

from services.data_service import version_up_file
from services.constants import WFA
from ui.components.extensions.message_box import MessageBox


from .base import Step

logger = logging.getLogger(__name__)


class PopulateVersionStep(Step):


    def __init__(self):
        super().__init__()

        self.message_box = MessageBox()

    def execute(self, ctx, callback):

        # print("inside PopulateVersionStep")
        page                    = ctx["page"] 
        dialog                  = page._active_dialog 
        current_working_version = ctx["working_version"]
        filename                = current_working_version["work_detail"]["file_name"]

        # selected_work_file   = self.current_working_version["work_detail"]["file_name"]
        # preview_file_name, _    = os.path.splitext(filename)
        
        preview_file_path      = ctx["preview_file_path"]
        preview_file           = os.path.basename(preview_file_path.as_posix())
        server_preview_path    = Path(current_working_version["server_preview_directory"]) / preview_file

        
      
        data_to_be_review = {
                               "preview_file"     : server_preview_path.as_posix(),
                               "work_file"        : (Path(current_working_version["server_work_directory"])/filename).as_posix(),
                            #    "process_dialog"   : page._active_dialog,
                               "file_sync_status" : WFA 
                            }

        # work_files_info = page.areas["work"]["file_widget"].task_data.get("work_files")
        work_files_info = ctx["work_files_info"]
        artist_slug     = ctx["artist_slug"]

        # artist_slug     = page.areas["work"]["file_widget"].task_data.get("artist_assigned").get("employee").get("slug")

        files_with_slug    = [file for file in work_files_info if file["slug"]]
        files_without_slug = [file for file in work_files_info if not file["slug"]]

        # print("line 36")
        if not files_without_slug:
            # page.message_box.show_message("No new versions to sync Thank U!", "error", "Send For Review Status")
            # self.message_box.show_message("No new versions to sync Thank U!", "error", "Send For Review Status")
            logger.debug("No new versions to sync.")
            if dialog:
                # print(dialog)
                dialog.close()
                page._active_dialog = None
            return

        latest_synced_version = max(
                                    files_with_slug,
                                    key=lambda x: int(re.search(r'_v(\d+)', x["work_detail"]["file_name"]).group(1)),
                                    default=None
                                )

        # print("line 619")
        # print("files with slug", len(files_with_slug))
        # print("files without slug", len(files_without_slug))
        # print("latest sync Version:", latest_synced_version)

        # latest_synced_version_slug = latest_synced_version["slug"] if latest_synced_version else page.last_sync_version_slug
        latest_synced_version_slug = latest_synced_version["slug"] if latest_synced_version else ctx["last_sync_version_slug"]
        # print("line 625 latest_synced_version_slug", latest_synced_version_slug)
        data_for_backend_version_up = []
        parent_slug = None
        
        for file in files_without_slug:
            # print("wothout slug")
            # print(file)
            file_path      = Path(file["work_detail"]["work_file"])
            last_saved     = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%d-%m-%Y %I:%M %p")
            file_size      = file_path.stat().st_size // (1024 * 1024)
            version_number = int(re.search(r'_v(\d+)', file["work_detail"]["file_name"]).group(1))
            # print("file with out slug", version_number)    

            if version_number == 0:
                continue

            parent_version = f"V{version_number-1:03}"
            parent_file    = next((f for f in files_with_slug if f["version"] == parent_version), None)
            # print("line 646 parent_file", parent_file)
            parent_slug    = parent_file["slug"] if parent_file else latest_synced_version_slug
            # print("line 648 parent_file", parent_slug)
            

            data_for_backend_version_up.append({
                "version_up_file": file_path.as_posix(),
                "last_saved_time": last_saved,
                "file_size": file_size,
            })

        final_data_to_be_send = {
                                    "artist_slug":       artist_slug,
                                    "file_slug":         parent_slug,
                                    "versions":          data_for_backend_version_up,
                                    "preview_file_path": data_to_be_review["preview_file"],
                                    "work_file_path":    data_to_be_review["work_file"],
                                    "file_sync_status":  data_to_be_review["file_sync_status"]
                                }


        # print("line 653")
        # pprint(final_data_to_be_send)

        logger.debug(f"Sending Version Up data to server: {final_data_to_be_send}")
        updated_task_data = version_up_file(final_data_to_be_send)

        # if page._active_dialog:
        #     page._active_dialog.close()

       
        if dialog:
            # print(dialog)
            dialog.close()
            page._active_dialog = None

        # if page._active_dialog:
        #     page._active_dialog.close()
        #     page._active_dialog = None

        # print(updated_task_data)

        if updated_task_data:
            page._sync_the_current_task(updated_task_data)
            callback(0)
        else:
            callback(1)

