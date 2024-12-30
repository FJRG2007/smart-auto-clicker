import os, platform
from src.utils.basics import get_config_path, get_resource_path, is_development_mode, get_current_executable_path

# Routes.
app_config_path = get_config_path()
app_config_file_path = os.path.join(app_config_path, "autoclicker_config.json")
app_assets_folder_path = get_resource_path("assets")
app_remote_data_path = f"{app_assets_folder_path}/remote.json"
app_icon_path = f"{app_assets_folder_path}/mouse.ico"
app_report_icon_path = f"{app_assets_folder_path}/report.png"

# Local.
local_is_developer_mode = is_development_mode()
local_app_exec_path = get_current_executable_path()
local_os_name = platform.system()

# Others
app_title = "Smart Auto Clicker - FJRG2007"