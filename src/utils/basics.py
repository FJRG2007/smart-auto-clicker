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

def get_current_executable_path():
    if getattr(sys, "frozen", False): current_path = os.path.abspath(sys.executable)
    else: current_path = os.path.abspath(__file__)
    if os.path.basename(current_path) == "basics.py": return os.path.join(os.path.dirname(os.path.dirname(current_path)), "../../init.py")
    return current_path

def is_development_mode():
    if hasattr(sys, "_MEIPASS"): return False
    executable_name = os.path.basename(sys.executable).lower()
    if "python" in executable_name or "py" in executable_name: return True
    return False