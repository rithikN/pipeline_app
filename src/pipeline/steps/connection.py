import logging
from services.data_service import check_VPN_connection, check_ftp_connection
from .base import Step

logger = logging.getLogger(__name__)

class ValidationConnectionStep(Step):
    def __init__(self):
        super().__init__()
    
    def execute(self, ctx, callback):
        page = ctx["page"]

        if not check_VPN_connection():
            if page._active_dialog:
                page._active_dialog.close()
            return callback(1)
        if not check_ftp_connection(check_FTP_conn=True):
            if page._active_dialog:
                page._active_dialog.close()
            return callback(1)
        
        return callback(0)  