from enum import Enum

# menu
APP_LABEL = 'App'
UPDATE_LABEL = 'Update App'
EXIT_LABEL = 'Exit'
HELP_LABEL = 'Help'
WIKI_LABEL = 'App Wiki'
ABOUT_LABEL = 'About'
ABOUT_INFO_LABEL = '3D Pipeline Application\nVersion 1.0\n© 2024 Philm CGI.'

EDIT_LABEL = 'Edit User Details'
LOGOUT_LABEL = 'Log Out'
DOWNLOAD_LABEL = 'Download Project Files'
EXIT_PROJECT_LABEL = 'Exit Project'

# form_page
TYPE = 'type'
LABEL = 'label'
ID = 'id'
OPTIONS = 'options'
FIELD_TYPE = Enum('FIELD_TYPE', ['lineedit', 'combobox', ])

# project_page
PROJECT_NAME = 'name'
PROJECT_TYPE = 'type'
THUMBNAIL_PATH = 'thumbnail'

# task_details
PREVIEW_PATH = 'preview_path'

# file_details
VIDEO_PATH = PREVIEW_PATH

# task_list
TASK_NAME = "name"
TASK_STATUS = "status"

# task_log
default_task_status_color = '#2b4463'
TASK_DETAIL_STATUS = TASK_STATUS
USERNAME = "username"
DATE = "date"
COMMENT = "comment"
STATUS_COLOR = "task_status_color"

# work_files
WORK_APP = "app"
WORK_VERSION = "version"
WORK_SIZE = "size"
WORK_DATE = "date"