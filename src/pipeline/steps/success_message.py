from typing import Optional

from PySide6.QtCore import QObject
from .base import Step

class SuccessMessageStep(Step):
    def __init__(self, 
                 signal_manager : Optional[QObject] = None,
                 refresh_app    = False
                 ):
        
        super().__init__()
        self.signal_manager  = signal_manager
        self.refresh_app     = refresh_app

    def execute(self, ctx, callback):
        page                = ctx["page"]
        message_box_title   = ctx["process_title"]

        _error_message = ""
        _is_error      = False
        
        if ctx.get("process") in ["REVIEW"]:
            report_message = f"File uploaded to Kitsu successfully : \n{ctx["preview_file_name"]} "
            report_message += f"\n\n⚠ NOTE : App will refresh !"
        elif ctx.get("process") in ["PUBLISH"]:
            report_message  = f"Task files published successfully :"
            report_message += f"\n{ctx["task_name"]}"
            report_message += f"\n\n⚠ NOTE : "
            report_message += f"\n- App will refresh !"
            report_message += f"\n- Published tasks will be removed from your list."
        else:
            _error_message  = "No message found for current pipeline process !"
            _error_message += "Please contact IT team."
            _is_error       = True
        
        if page._active_dialog:
            page._active_dialog.close()

        if _is_error:
            page.message_box.show_message(_error_message, "error", message_box_title)
            return callback(1)
        else:
            page.message_box.show_message(report_message, "info", message_box_title)
            print(f"\n ------ >>> {report_message}\n")
            if self.refresh_app:
                self.signal_manager.refresh_triggered.emit()
            return callback(0)   