from enum import Enum

# menu
APP_LABEL = 'App'
UPDATE_LABEL = 'Update App'
EXIT_LABEL = 'Exit'
HELP_LABEL = 'Help'
WIKI_LABEL = 'App Wiki'
ABOUT_LABEL = 'About'
ABOUT_INFO_LABEL = '3D Pipeline Application\nVersion 1.0\n© 2025 Philm CGI.'

EXCLUDE_MAC_FILES = [".DS_Store"]

EDIT_LABEL = 'Edit User Details'
LOGOUT_LABEL = 'Log Out'
DOWNLOAD_LABEL = 'Download Project Files'
EXIT_PROJECT_LABEL = 'Exit Project'

# login_page
USER_ID = 'user'
USER_LABEL = 'Username'
USER_PLACEHOLDER = 'User ID'
PASS_ID = 'pass'
PASS_LABEL = 'Password'
PASS_PLACEHOLDER = '•••••••••••••••••'

# form_page
TYPE = 'type'
LABEL = 'label'
ID = 'id'
OPTIONS = 'options'
FIELD_TYPE = Enum('FIELD_TYPE', ['lineedit', 'combobox', ])

# project_page
PROJECT_NAME = 'name'
PROJECT_TYPE = 'production_type'
PROJECT        = "project"
PROJECT_SLUG   = "slug"
ARTIST_SLUG    = "artist_slug"

# task_details
PREVIEW_PATH = 'local_preview_path'


# file_details
VIDEO_PATH = PREVIEW_PATH
VALID_VIDEO_FORMATS = [".mp4",".mov"]

# task_list
TASK_SLUG                    = "slug"
TASK_NAME                    = "name"
TASK_STATUS                  = "task_status"
TASK_STATUS_NAME             = "short_name"
TASK_STATUS_COLOR            = "color"
TASK_SHOT_DETAIL             = "shot_detail"
TASK_SHOT_SEQ_DETAIL         = "sequence_details"
TASK_SHOT_SEQ_NAME           = "sequence_number"
TASK_SHOT_SEQ_EPISODE_DETAIL = "episode_details"
TASK_SHOT_SEQ_EPISODE_NAME   = "name"
TASK_ASSIGNED                = "artist_assigned"
TASK_EMPLOYEE                = "employee"
TASK_EMPLOYEE_NAME           = "employee_name"
TASK_START_DATE              = "start_date"
TASK_END_DATE                = "end_date"
TASK_EMPLOYEE_SLUG           = "slug"


#CREATE File Record
CREATE_FILE_TASK_SLUG       = "task_slug"
CREATE_FILE_USER_SLUG       = "user_slug"
CREATE_FILE_PLATFORM_KEY    = "platform_key"
CREATE_FILE_PLATFORM_HOME   = "platform_home"


# task_log
default_task_status_color = '#2b4463'
TASK_DETAIL_STATUS = TASK_STATUS
FILE_APP                     = "app_name"
FILE_SIZE                    = "file_size"
FILE_DATE                    = "date"
FILE_VERSION                 = "version"


LOG_USERNAME                 = "username"
LOG_STATUS                   = "status"
LOG_DATE                     = "date"
LOG_COMMENT                  = "comment"
LOG_STATUS_COLOR             = "task_status_color"


USERNAME = "username"
DATE = "date"
COMMENT = "comment"
STATUS_COLOR = "task_status_color"

# work_files
WORK_APP = "app_name"
WORK_VERSION = "version"
WORK_SIZE = "file_size"
WORK_DATE = "date"
WORK_FILES = "work_files"
WORK_FILE_DETAIL = "work_detail"
WORK_FILE_NAME = "file_name"
WORK_FILE_TYPE = "file_type"
APPROVED = "approved"
PUBLISHED = 'published'
PUB       = 'PUB'
WFA       = "WFA"

DEFAULT_FOLDER_KEY = "01_work"
FOLDER_KEY         = "folder_key"

SKIP_DATA = ["app_executable_path", "file_type", "ftp_path", "preview_formats", "locked_status", "mac_executable_path"]

SOFTWARE_ICON_DATA = {
                        ".blend"    : "resources/icons/work_list/software/blender.svg",             # Blender
                        ".aep"      : "resources/icons/work_list/software/afterfx.svg",             # After Effects
                        ".drp"      : "resources/icons/work_list/software/davinci.svg",             # DaVinci
                        ".ma"       : "resources/icons/work_list/software/maya.svg",                # Maya
                        ".mb"       : "resources/icons/work_list/software/maya.svg",                # Maya
                        ".nk"       : "resources/icons/work_list/software/nuke.svg",                # Nuke
                        ".psd"      : "resources/icons/work_list/software/photoshop.svg",           # Adobe Photoshop
                        ".moho"     : "resources/icons/work_list/software/moho.svg",                # Moho
                        ".tvpp"     : "resources/icons/work_list/software/tvpaint.svg",             # TVPaint
                    }
