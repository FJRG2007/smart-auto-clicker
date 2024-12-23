from .config_window import ConfigWindow

class WindowsManager:
    def __init__(self, parent, config_file):
        self.parent = parent
        self.config_file = config_file
        self.config_window = None

    def open_config_window(self):
        if self.config_window is None or not self.config_window.window.winfo_exists(): self.config_window = ConfigWindow(self.parent, self.config_file)
        else: self.config_window.window.lift()