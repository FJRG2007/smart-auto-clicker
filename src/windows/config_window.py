from tkinter import ttk, messagebox
from src.memory import MemoryManager
from src.driver.executions import enable_startup, disable_startup
import json, time, tkinter as tk, requests, webbrowser, src.lib.globals as globals

class ConfigWindow:
    CACHE_TIMEOUT = 60

    def __init__(self, parent):
        self.parent = parent
        self.cache = {"data": None, "timestamp": 0}
        self.window = tk.Toplevel(self.parent)
        self.window.title("Settings")
        self.window.geometry("300x300")
        self.window.resizable(False, False)

        # Icon.
        self.window.iconbitmap(globals.app_icon_path)

        # Load existing configuration from the config file.
        self.config = self.load_config()
        self.original_config = self.config.copy()
        self.config_changed = False

        # Frame to group the Auto-position option and its note.
        auto_position_frame = ttk.Frame(self.window)
        auto_position_frame.pack(pady=10, fill="x", padx=10)

        # Variable to track the checkbox state.
        self.auto_position_var = tk.BooleanVar(value=self.config.get("use_current_pos", True))

        # Checkbutton to enable/disable auto-positioning.
        auto_position_checkbox = ttk.Checkbutton(
            auto_position_frame, 
            text="Enable auto-positioning of window", 
            variable=self.auto_position_var,
            command=self.on_config_change
        )
        auto_position_checkbox.pack(anchor="w")

        # Informative note about the option.
        note_label = ttk.Label(auto_position_frame, 
            text="Note: Enabling this may affect startup speed.", 
            font=("Arial", 8), anchor="w", justify="left")
        note_label.pack(anchor="w")

        # Variable to track the startup mode state.
        self.startup_mode_var = tk.StringVar(value=self.config.get("startup_mode", "normal"))

        # Frame to group the startup mode options.
        startup_mode_frame = ttk.Frame(self.window)
        startup_mode_frame.pack(pady=10, fill="x", padx=10)

        # Label for startup mode.
        startup_mode_label = ttk.Label(startup_mode_frame, text="Startup Mode:")
        startup_mode_label.pack(anchor="w")

        # Radio buttons for startup mode options.
        normal_radio = ttk.Radiobutton(
            startup_mode_frame, 
            text="Normal", 
            variable=self.startup_mode_var, 
            value="normal",
            command=self.on_config_change
        )
        normal_radio.pack(anchor="w")

        minimized_radio = ttk.Radiobutton(
            startup_mode_frame, 
            text="Minimized", 
            variable=self.startup_mode_var, 
            value="minimized",
            command=self.on_config_change
        )
        minimized_radio.pack(anchor="w")

        tray_radio = ttk.Radiobutton(
            startup_mode_frame, 
            text="Tray", 
            variable=self.startup_mode_var, 
            value="tray",
            command=self.on_config_change
        )
        tray_radio.pack(anchor="w")

        # Frame for the "Startup on boot" option.
        startup_frame = ttk.Frame(self.window)
        startup_frame.pack(pady=10, fill="x", padx=10)

        # Variable to track the "Exec on startup" state.
        self.startup_var = tk.BooleanVar(value=self.config.get("exec_on_startup", False))

        # Checkbox for enabling/disabling execution on startup.
        startup_checkbox = ttk.Checkbutton(
            startup_frame,
            text="Run application on system startup",
            variable=self.startup_var,
            command=self.on_startup_change
        )
        startup_checkbox.pack(anchor="w")

        startup_note = ttk.Label(
            startup_frame,
            font=("Arial", 8),
            anchor="w", 
            justify="left"
        )
        startup_note.pack(anchor="w", pady=(2, 0))

        if globals.local_is_developer_mode: startup_note.config(text="ⓘ This option does not work in development mode.", foreground="red")
        else: startup_note.config(text="This feature is in beta.", foreground="gray")

        self.update_label = ttk.Label(self.window, text="Loading...", foreground="blue")
        self.update_label.pack(pady=5)

        self.check_for_updates()

        # Button to save and close.
        save_button = ttk.Button(self.window, text="Save and Exit", command=self.save_and_exit)
        save_button.pack(side="left", padx=10, pady=10)

        # Button to exit without saving.
        cancel_button = ttk.Button(self.window, text="Exit Without Saving", command=self.exit_without_saving)
        cancel_button.pack(side="right", padx=10, pady=10)

        # Bind window close (X) event to check for unsaved changes.
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def check_for_updates(self):
        if time.time() - self.cache["timestamp"] < self.CACHE_TIMEOUT: self.process_update_data(self.cache["data"])
        else:
            self.update_label.config(text="Loading...", foreground="blue")
            self.window.update_idletasks()
            self.window.after(70, self.fetch_update_data)

    def fetch_update_data(self):
        try:
            response = requests.get("https://github.com/FJRG2007/smart-auto-clicker/raw/refs/heads/main/assets/remote.json")
            if response.status_code == 200:
                remote_data = response.json()
                self.cache = {"data": remote_data, "timestamp": time.time()}
                self.process_update_data(remote_data)
            else: self.update_label.config(text="Failed to check for updates.", foreground="red")
        except Exception as e:
            self.update_label.config(text="Error checking for updates.", foreground="red")
            print(f"Error checking for updates: {e}")

    def process_update_data(self, remote_data):
        with open(globals.app_remote_data_path, "r") as f:
            current_version = json.load(f).get("version", "error")
        remote_version = remote_data.get("version", "")
        download_url = remote_data.get("download_url", "https://github.com/FJRG2007/smart-auto-clicker/releases")
        if remote_version and remote_version != current_version:
            self.update_label.config(text=f"New version available: {remote_version}", foreground="red")
            update_button = ttk.Button(self.window, text="Update", command=lambda: webbrowser.open(download_url))
            update_button.pack(pady=5, ipadx=10, fill="x", anchor="center", expand=True)
        else: self.update_label.config(text="You are using the latest version.", foreground="green")

    def on_startup_change(self):
        self.config_changed = True
        self.config["exec_on_startup"] = self.startup_var.get()

    def on_config_change(self):
        self.config_changed = True

    def save_config(self):
        # Gather the configuration data.
        new_config = {
            "use_current_pos": self.auto_position_var.get(),
            "startup_mode": self.startup_mode_var.get(),
            "exec_on_startup": self.startup_var.get()
        }
        try:
            with open(globals.app_config_file_path, "r") as f:
                current_config = json.load(f)
            current_config["use_current_pos"] = new_config["use_current_pos"]
            current_config["startup_mode"] = new_config["startup_mode"]
            current_config["exec_on_startup"] = new_config["exec_on_startup"]
            with open(globals.app_config_file_path, "w") as f:
                json.dump(current_config, f)
            MemoryManager.set("use_current_pos", new_config["use_current_pos"])
            MemoryManager.set("startup_mode", new_config["startup_mode"])
            MemoryManager.save_memory()
            self.original_config = new_config.copy()
            # Apply the changes to the system.
            if new_config["exec_on_startup"]: enable_startup()
            else: disable_startup()
            self.config_changed = False
        except Exception as e: messagebox.showerror("Error", f"Error saving configuration:\n{e}")

    def load_config(self):
        # Try to load the configuration from a file.
        try:
            with open(globals.app_config_file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or is corrupt, return default values.
            return {
            "hours": "0",
            "minutes": "0",
            "seconds": "0",
            "milliseconds": "100",
            "click_key": "left",
            "use_current_pos": True,
            "startup_mode": "normal",
            "click_pos": [0, 0],
            "trigger_key": "F6",
            "hold_mode": False,
            "hold_duration": "0.1",
            "window_x": 100,
            "window_y": 100
        }

    def save_and_exit(self):
        # Save the settings and then close the window.
        self.save_config()
        self.window.destroy()

    def exit_without_saving(self):
        # Close the window without saving.
        self.window.destroy()

    def on_close(self):
        # Prompt the user before closing without saving, only if there are unsaved changes.
        if self.config_changed:
            if messagebox.askokcancel("Quit", "Do you want to exit without saving changes?"): self.window.destroy()
        else: self.window.destroy()

    # Method to get the auto-positioning setting.
    def get_auto_position(self):
        return self.auto_position_var.get()

    # Method to get the startup mode setting.
    def get_startup_mode(self):
        return self.startup_mode_var.get()