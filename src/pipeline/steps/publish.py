from services.data_service import publish_file
from pipeline.utils.debug import debug_tools

from .base import Step

class PublishFileStep(Step):
    def execute(self, ctx, callback):
        # print("Inside PublishFileStep")
        page    = ctx["page"]
        slug    = ctx["working_version"]["slug"]
        data    = {"file_record_slug": slug}
        updated_task_data = publish_file(data)
        message_box_title   = ctx["process_title"] + " : Publish File Step"
        # report_message = None
        
        # if page._active_dialog:
        #     page._active_dialog.close()
        # if updated_task_data:
        #     report_message = "Files published successfully."
        #     page.message_box.show_message(report_message, "info", "Send For Publish Status")
        # else:
        #     page.message_box.show_error("Error while publish files in the server.")

        _error_message = ""
        _is_error      = False

        if not updated_task_data:
            _error_message  = "Error while updating publish data to Database"
            _error_message += "Please contact IT team."
            _is_error       = True
        
        if _is_error:
            page.message_box.show_message(_error_message, "error", message_box_title)
            if page._active_dialog:
                page._active_dialog.close()
            return callback(1)
        else:
            return callback(0)    