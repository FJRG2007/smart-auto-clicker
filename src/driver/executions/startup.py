from tkinter import messagebox
import os, src.lib.globals as globals

def enable_startup():
    try:
        if globals.local_os_name == "Windows":
            import winreg
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
                    try:
                        current_value = winreg.QueryValueEx(key, globals.app_title)[0]
                        if current_value != globals.local_app_exec_path:
                            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as write_key:
                                winreg.SetValueEx(write_key, globals.app_title, 0, winreg.REG_SZ, globals.local_app_exec_path)
                    except FileNotFoundError:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as write_key:
                            winreg.SetValueEx(write_key, globals.app_title, 0, winreg.REG_SZ, globals.local_app_exec_path)
            except Exception as e: messagebox.showerror("Error", f"Failed to enable startup:\n{e}")
        elif globals.local_os_name == "Darwin": # macOS
            plist_path = f"{os.path.expanduser('~')}/Library/LaunchAgents/{globals.app_title}.plist"
            plist_content = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>Label</key>
                <string>{globals.app_title}</string>
                <key>ProgramArguments</key>
                <array>
                    <string>{globals.local_app_exec_path}</string>
                </array>
                <key>RunAtLoad</key>
                <true/>
            </dict>
            </plist>
            """
            with open(plist_path, "w") as plist_file:
                plist_file.write(plist_content)
            os.system(f"launchctl load {plist_path}")
        elif globals.local_os_name == "Linux":
            autostart_path = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_path, exist_ok=True)
            desktop_entry_path = os.path.join(autostart_path, f"{globals.app_title}.desktop")
            desktop_entry_content = f"""
            [Desktop Entry]
            Type=Application
            Exec={globals.local_app_exec_path}
            Hidden=false
            NoDisplay=false
            X-GNOME-Autostart-enabled=true
            Name={globals.app_title}
            """
            with open(desktop_entry_path, "w") as desktop_file:
                desktop_file.write(desktop_entry_content)
        else: messagebox.showerror("Error", "Unsupported operating system for startup.")
    except Exception as e: messagebox.showerror("Error", f"Failed to enable startup:\n{e}")

def disable_startup():
    try:
        if globals.local_os_name == "Windows":
            import winreg
            reg_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, globals.app_title)
        elif globals.local_os_name == "Darwin": # macOS
            plist_path = f"{os.path.expanduser('~')}/Library/LaunchAgents/{globals.app_title}.plist"
            if os.path.exists(plist_path):
                os.system(f"launchctl unload {plist_path}")
                os.remove(plist_path)
        elif globals.local_os_name == "Linux":
            desktop_entry_path = os.path.expanduser(f"~/.config/autostart/{globals.app_title}.desktop")
            if os.path.exists(desktop_entry_path): os.remove(desktop_entry_path)
        else: messagebox.showerror("Error", "Unsupported operating system for startup.")
    except Exception as e: messagebox.showerror("Error", f"Failed to disable startup:\n{e}")