import os, sys

def get_resource_path(relative_path) -> str:
    try: base_path = sys._MEIPASS
    except AttributeError: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_config_path():
        if os.name == "nt": base_dir = os.getenv("APPDATA", os.path.expanduser("~"))
        else: base_dir = os.path.expanduser("~/.config")
        config_dir = os.path.join(base_dir, "FJRG2007_projects_data", "SmartAutoClicker")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir