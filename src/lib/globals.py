import os
from src.utils.basics import get_config_path, get_resource_path

# Routes.
app_config_path = get_config_path()
app_config_file_path = os.path.join(app_config_path, "autoclicker_config.json")
app_assets_folder_path = get_resource_path("assets")
app_remote_data_path = f"{app_assets_folder_path}/remote.json"
app_icon_path = f"{app_assets_folder_path}/mouse.ico"
app_report_icon_path = f"{app_assets_folder_path}/report.png"