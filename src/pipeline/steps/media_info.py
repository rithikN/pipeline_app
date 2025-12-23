from pprint import pprint

from .base import Step
from services.data_service import fetch_data_from_kitsu

from pipeline.utils.media_utils import get_mediainfo_data
from pipeline.utils.debug import debug_tools
from ui.components.extensions.message_box import MessageBox

class ValidateMediaInfo(Step):
    def __init__(self):
        super().__init__()
        self.message_box = MessageBox()

    def execute(self, ctx, callback):
        wf                          = ctx["working_version"]
        page                        = ctx["page"]
        process                     = ctx.get("process")
        preview_file_path           = ctx["preview_file_path"]        
        template_file_fps           = 24    ### Fps is currently hardcoded, needs to be fetched from ctx data (Bhanu needs to look into this !)

        preview_file_data   = get_mediainfo_data(preview_file_path)
        preview_file_type   = preview_file_data['tracks'][1]['track_type']
        preview_file_width  = preview_file_data['tracks'][1]['width']
        preview_file_height = preview_file_data['tracks'][1]['height']

        kitsu_data          = {"project" : wf["project"], "sequence" : wf["sequence"], "shot" : wf["shot"]}
        kitsu_response      = fetch_data_from_kitsu(kitsu_data)
        kitsu_frame_count   = kitsu_response['data']['shot_data']['nb_frames']

        is_error      = False
        error_message = "Preview file validation failed ! \n\n"

        if process == "REVIEW":
            template_file_width         = ctx["template_file_resolution"].split("X")[0]
            template_file_height        = ctx["template_file_resolution"].split("X")[1]
        if process == "PUBLISH":
            template_file_width         = ctx["publish_file_resolution"].split("X")[0]
            template_file_height        = ctx["publish_file_resolution"].split("X")[1]


        if not int(preview_file_width) >= int(template_file_width) or not int(preview_file_height) >= int(template_file_height):
            error_message += f"Current file resolution   : {preview_file_width}x{preview_file_height}\n"
            error_message += f"Required file resolution : {template_file_width}x{template_file_height}"
            is_error = True

        if preview_file_type == "Video":
            preview_file_fps = int(float(preview_file_data['tracks'][1]['frame_rate']))
            preview_frame_count = int(preview_file_data['tracks'][1]['frame_count'])

            if preview_file_fps != template_file_fps:
                if is_error:
                    error_message += "\n\n"
                error_message += f"Current file fps   : {preview_file_fps}\n"
                error_message += f"Required file fps : {template_file_fps}"
                is_error = True
            if preview_frame_count != kitsu_frame_count:
                if is_error:
                    error_message += "\n\n"
                error_message += f"Current frame count   : {preview_frame_count}\n"
                error_message += f"Required frame count : {kitsu_frame_count}"
                is_error = True

        if is_error:
            self.message_box.show_message(error_message, "error", "Media Info Validation Error")
            if page._active_dialog:
                page._active_dialog.close()
            return callback(1)
        else:
            return callback(0)