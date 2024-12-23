from tkinter import ttk, messagebox
from src.memory import MemoryManager
from src.utils.basics import get_resource_path
import json, time, tkinter as tk, requests, webbrowser

class ConfigWindow:
    CACHE_TIMEOUT = 60

    def __init__(self, parent, config_file):
        self.parent = parent
        self.config_file = config_file
        self.cache = {"data": None, "timestamp": 0}
        self.window = tk.Toplevel(self.parent)
        self.window.title("Settings")
        self.window.geometry("300x250")
        self.window.resizable(False, False)

        # Load existing configuration from the config file.
        self.config = self.load_config()
        self.original_config = self.config.copy()
        self.config_changed = False

        # Label for settings.
        label = ttk.Label(self.window, text="Settings go here")
        label.pack(pady=20)

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
            self.window.after(100, self.fetch_update_data)

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
        with open(get_resource_path("assets/remote.json"), "r") as f: 
            current_version = json.load(f).get("version", "error")
        remote_version = remote_data.get("version", "")
        download_url = remote_data.get("download_url", "https://github.com/FJRG2007/smart-auto-clicker/releases")
        if remote_version and remote_version != current_version:
            self.update_label.config(text=f"New version available: {remote_version}", foreground="red")
            update_button = ttk.Button(self.window, text="Update", command=lambda: webbrowser.open(download_url))
            update_button.pack(pady=5, ipadx=10, fill="x", anchor="center", expand=True)
        else: self.update_label.config(text="You are using the latest version.", foreground="green")

    def on_config_change(self):
        self.config_changed = True

    def save_config(self):
        # Gather the configuration data.
        new_config = {
            "use_current_pos": self.auto_position_var.get()
        }
        try:
            with open(self.config_file, "r") as f:
                current_config = json.load(f)
            current_config["use_current_pos"] = new_config["use_current_pos"]
            with open(self.config_file, "w") as f:
                json.dump(current_config, f)
            MemoryManager.set("use_current_pos", new_config["use_current_pos"])
            MemoryManager.save_memory()
            self.original_config = new_config.copy()
            self.config_changed = False
        except Exception as e: messagebox.showerror("Error", f"Error saving configuration:\n{e}")

    def load_config(self):
        # Try to load the configuration from a file.
        try:
            with open(self.config_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or is corrupt, return default values.
            return {
                "use_current_pos": True,
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
