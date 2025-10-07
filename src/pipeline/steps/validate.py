import os, logging
from pathlib import Path
from pprint import pprint

from services.file_ops import collect_local_files
from services.constants import WFA, PUBLISHED, APPROVED

from pipeline.utils.preview_utils import verify_and_return_preview_file
from pipeline.utils.publish_utils import verify_and_return_publish_format
from pipeline.utils.path_utils import split_from_version_simple
from pipeline.utils.debug import debug_tools

from ui.components.extensions.message_box import MessageBox

from .base import Step
message_box = MessageBox()
logger      = logging.getLogger(__name__) 


class ValidateFoldersStep(Step):
    def __init__(self):
        super().__init__()
        self.message_box = MessageBox()

    def execute(self, ctx, callback):
        # print(f"\n ------ >>> DEBUG_TOOLS :\n --- {debug_tools()}")
        # pprint(current_working_version)
        page                    = ctx["page"]
        current_working_version = ctx["working_version"]
        current_task_version    = current_working_version["version"].lower()
        local_output_directory  = current_working_version["local_output_directory"]
        server_output_directory = current_working_version["ftp_output_directory"]
        working_folder_parts    = Path(current_working_version["work_detail"]["work_file"]).parent.parts
        message_box_title       = ctx["process_title"] + " : Validate Folder Step"

        

        _error_message = ""
        _is_error      = False

        if current_working_version["sequence"] not in working_folder_parts:
            _error_message  = f"The given working folder does not have Sequence {current_working_version["sequence"]}"
            _is_error       = True
        
        if not _is_error:
            if ctx.get("process") in ["PUBLISH"]:
                ctx["local_publish_dir"]  = Path(local_output_directory) / current_task_version
                ctx["server_publish_dir"] = Path(server_output_directory) / current_task_version
                if not ctx["local_publish_dir"].exists():
                    os.makedirs(ctx["local_publish_dir"], exist_ok=True)
        
        if _is_error:
            page.message_box.show_message(_error_message, "error", message_box_title)
            if page._active_dialog:
                page._active_dialog.close()
            return callback(1)
        else:
            return callback(0)    


class ValidateFilesStep(Step):
    def __init__(self):
        super().__init__()
        self.message_box = MessageBox()
    
    def execute(self, ctx, callback):
        # print("line 14 inside ValidateFilesStep")
        page                = ctx["page"]
        wf                  = ctx["working_version"]
        message_box_title   = ctx["process_title"] + " : Validate File Step"

        _error_message = ""
        _is_error      = False

        if not ctx["work_files_info"]:  
            _error_message  = "Failed to fetch Work File data !"
            _error_message += "\n\nIf issue persists, contact IT team."
            _is_error       = True
        else:
            if not next((file.get("slug") for file in ctx["work_files_info"] if file.get("version").casefold() == "v000"), None):
                _error_message  = "File records not found ! \n\nTo fix this issue : \nRight click on any work file and click on \n'Create v000 File'."
                _error_message += "\n\nIf issue persists, contact IT team."
                _is_error       = True

        if not _is_error:
            if wf.get("version").casefold() == "v000":    
                _error_message  = "V000 file cannot be submitted for review ! \nPlease create a new version and try again."
                _error_message += "\n\nIf issue persists, contact IT team."
                _is_error       = True
        
        # if not _is_error:
        #     if ctx.get("process") in ["REVIEW"]:
        #         if wf.get("status") == APPROVED:
        #             _error_message  = "Selected file version is already Approved !"
        #             _error_message += "\n\nContact Production team to change status."
        #             _is_error       = True
        #         elif wf.get("status") == PUBLISHED:
        #             _error_message  = "Selected file version is already Published !"
        #             _error_message += "\n\nContact Production team to change status."
        #             _is_error       = True

        # if not _is_error:
        #     if ctx.get("process") in ["PUBLISH"]:
        #         if wf.get("status") != APPROVED:
        #             if wf.get("status") == PUBLISHED:
        #                 _error_message  = "Selected File Version is already Published !"
        #                 _error_message += "\n\nContact Production team to change status."
        #                 _is_error       = True
        #             else:
        #                 _error_message  = "Selected File Version is not Approved yet!"
        #                 _error_message += "\n\nContact Production team to change status."
        #                 _is_error       = True

        if not _is_error:
            if not self.validate_files(ctx, wf):
                _error_message  = "Work/Preview file validation failed for Send to Review."
                _error_message += "\n\nIf issue persists, contact IT team."
                _is_error       = True
            
        # if not _is_error:
            # if not self.validate_folders():
            #     logger.debug("Work/Preview/Output Folders validation failed for Send to Review.")
            #     if self._active_dialog:
            #         self._active_dialog.close()
            #     return        

        #### Get preview file name, path and extention
        selected_work_file   = wf["work_detail"]["file_name"]
        work_file_name, work_file_ext = os.path.splitext(selected_work_file)
        
        ctx["preview_file_path"], ctx["template_file_resolution"]    = verify_and_return_preview_file(wf, work_file_name)
        if not ctx["preview_file_path"]:
            supported_preview_formats = wf["work_detail"]["preview_formats"]
            preview_format_list  = [list(d.keys())[0] for d in supported_preview_formats]
            if len(preview_format_list) > 1:
                _error_message  = f"Preview file not found : \n{work_file_name}.{preview_format_list} \n\nPlease save the file in 02_Preview folder."
                _is_error       = True
            else:
                _error_message  = f"Preview file not found : \n{work_file_name}.{preview_format_list[0]} \n\nPlease save the file in 02_Preview folder"
                _is_error       = True
        else:
            ctx["preview_file_name"] = Path(ctx["preview_file_path"]).name
        
        if ctx.get("process") in ["PUBLISH"]:
            ctx["publish_file_resolution"] = verify_and_return_publish_format(wf, ctx["preview_file_name"])

        if _is_error:
            page.message_box.show_message(_error_message, "error", message_box_title)
            if page._active_dialog:
                page._active_dialog.close()
            return callback(1)
        else:
            return callback(0)                    

    # ------------------------------------------------------------
    #  VALIDATION METHOD
    # ------------------------------------------------------------
    def validate_files(self, ctx, working_version) -> bool:
        """
        Checks if the local work file path is valid and exists on disk.
        Returns True if valid, False if not.
        """

        if not working_version:
            self.message_box.show_error("No current working version is set.")
            return False

        local_file = working_version["work_detail"]["work_file"]

        if not local_file:
            self.message_box.show_error("No local work file path found. Please check and try again.")
            return False


        local_path = Path(local_file)


        file_name = local_path.name
        prefix, version_and_ext = split_from_version_simple(file_name)
        if  prefix != ctx["task_name"]:
            # print("line 774")
            self.message_box.show_error(f"Local work file name does not match with the Task Name: {local_path}")
            return False


        if not local_path.is_file():
            self.message_box.show_error(f"Local work file does not exist: {local_path}")
            return False

        # pprint(self.current_working_version)
        # print("line 708",local_path)
        if local_path.suffix not in working_version["work_detail"]["file_type"]:
            self.message_box.show_error(f"Unsupported file type {local_path.suffix} found in 01_Work Folder")
            return False


        local_work_files = collect_local_files(working_version)

        for file_path in local_work_files:
            if file_path.suffix not in working_version["dcc_app"]["output_format"]:
                self.message_box.show_error(f"Unsupported file type {file_path.suffix} found in 01_Work Folder")
                return False
      
        return True    
