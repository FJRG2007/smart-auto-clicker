import json
import tkinter as tk
from tkinter import ttk, messagebox
from src.memory import MemoryManager

class ConfigWindow:
    def __init__(self, parent, config_file):
        self.parent = parent
        self.config_file = config_file
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

        # Button to save and close.
        save_button = ttk.Button(self.window, text="Save and Exit", command=self.save_and_exit)
        save_button.pack(side="left", padx=10, pady=10)

        # Button to exit without saving.
        cancel_button = ttk.Button(self.window, text="Exit Without Saving", command=self.exit_without_saving)
        cancel_button.pack(side="right", padx=10, pady=10)

        # Bind window close (X) event to check for unsaved changes.
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_config_change(self):
        self.config_changed = True

    def save_config(self):
        # Gather the configuration data.
        config = {
            "use_current_pos": self.auto_position_var.get(),
            "window_x": self.parent.winfo_x(),
            "window_y": self.parent.winfo_y()
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
            MemoryManager.set("use_current_pos", config["use_current_pos"])
            MemoryManager.save_memory()
            self.original_config = config.copy() # Update the original config after saving.
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
