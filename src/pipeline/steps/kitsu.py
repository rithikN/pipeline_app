
import os, re, logging
from pathlib import Path
from pprint import pprint

from services.data_service import upload_to_kitsu
from .base import Step
from services.constants import (
    PROJECT, PROJECT_NAME, PROJECT_SLUG, ARTIST_SLUG,
    WORK_FILES, APPROVED, PUBLISHED, WFA, EXCLUDE_MAC_FILES, PUB
)

logger = logging.getLogger(__name__)

class UpdateKitsuStep(Step):
    
    def __init__(self, status):
        self.status  = status
        self.context = None


    def execute(self, ctx, callback):
        # print("Inside UpdateKitsuStep")
        page         = ctx["page"]
        wf           = ctx["working_version"]
        preview      = ctx.get("server_preview_path")
        process      = ctx.get("process")
        self.context = ctx 


        artist_name    = ctx["artist_name"]
        preview_file   = ctx["preview_file_path"]

        server_preview = Path(wf["server_preview_directory"]) / preview_file

        if process == "REVIEW":
            preview_file   = os.path.basename(ctx["preview_file_path"].as_posix())
            server_preview = Path(wf["server_preview_directory"]) / preview_file
            comment        = f" {ctx["artist_name"]} uploaded file {preview_file} for review."
            self._update_data_to_kitsu(server_preview, comment, WFA)
        
        elif process == "PUBLISH":
            selected_work_file = wf["work_detail"]["file_name"]
            comment            = f"{ctx["artist_name"]} published file {selected_work_file} to the Server"
            self._update_data_to_kitsu(None, comment, PUB)

        
        callback(0)
        # callback(0 if not kitsu_response.get("status") else 1)
        # callback(0 if not kitsu_response.get("status") else 1)

    def _update_data_to_kitsu(self, preview_file_path, comment, task_status):
        kitsu_data = {
                        "project"    : self.context["working_version"]["project"],
                        "sequence"   : self.context["working_version"]["sequence"],
                        "shot"       : self.context["working_version"]["shot"],
                        "task_type"  : self.context["working_version"]["task_type"],
                        "task_status": task_status,
                        "comment"    : comment
                    }
       
        if preview_file_path:
            # match = re.search(r'\d+', str(preview_file_path))
            match = re.search(r'_v(\d+)', str(preview_file_path.as_posix()))
            if match:
                kitsu_data["preview_version"] = int(match.group(1))
            kitsu_data["preview"] = str(preview_file_path.as_posix())
        logger.info(f"Sending Kitsu data: {kitsu_data}")
        kitsu_response = upload_to_kitsu(kitsu_data)
        logger.info(f"Kitsu response: {kitsu_response}")
        return kitsu_response.get("status", False)    
    



class ValidateTaskStatusStep(Step):
        
    def __init__(self):
        super().__init__()
    
    def execute(self, ctx, callback):

        page                = ctx["page"]
        wf                  = ctx["working_version"]
        message_box_title   = ctx["process_title"] + " : Validate Task Status Step"

        _error_message = ""
        _is_error      = False

        if not _is_error:
            if ctx.get("process") in ["REVIEW"]:
                if wf.get("status") == APPROVED:
                    _error_message  = "Selected file version is already Approved !"
                    _error_message += "\n\nContact Production team to change status."
                    _is_error       = True
                elif wf.get("status") == PUBLISHED:
                    _error_message  = "Selected file version is already Published !"
                    _error_message += "\n\nContact Production team to change status."
                    _is_error       = True

        if not _is_error:
            if ctx.get("process") in ["PUBLISH"]:
                if wf.get("status") != APPROVED:
                    if wf.get("status") == PUBLISHED:
                        _error_message  = "Selected File Version is already Published !"
                        _error_message += "\n\nContact Production team to change status."
                        _is_error       = True
                    else:
                        _error_message  = "Selected File Version is not Approved yet!"
                        _error_message += "\n\nContact Production team to change status."
                        _is_error       = True
        if _is_error:
            page.message_box.show_message(_error_message, "error", message_box_title)
            if page._active_dialog:
                page._active_dialog.close()
            return callback(1)
        else:
            return callback(0)         
        # page = ctx["page"]

        # if not check_VPN_connection():
        #     if page._active_dialog:
        #         page._active_dialog.close()
        #     return callback(1)
        # if not check_ftp_connection(check_FTP_conn=True):
        #     if page._active_dialog:
        #         page._active_dialog.close()
        #     return callback(1)
        
        # return callback(0)  
