from threading import Thread
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
from keyboard import hook, unhook_all
import os, json, time, mouse, tkinter as tk, requests, keyboard

class AutoClicker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("Smart Auto Clicker - FJRG2007")
        self.root.geometry("400x670")
        self.root.resizable(False, False)

        self.config_path = self.get_config_path()

        # Icon.
        self.icon_file = os.path.join(self.config_path, "mouse.ico")
        if os.path.exists(self.icon_file): self.root.iconbitmap(self.icon_file)
        else:
            response = requests.get("https://raw.githubusercontent.com/FJRG2007/smart-auto-clicker/refs/heads/main/assets/mouse.ico")
            if response.status_code == 200:
                with open(self.icon_file, "wb") as file:
                    file.write(response.content)
                self.root.iconbitmap(self.icon_file)
            else: print(f"Error downloading image. Status code: {response.status_code}")
        
        # Variables.
        self.is_running = False
        self.click_thread = None
        self.trigger_key = "F6"
        self.click_key = "left"
        self.use_current_pos = True
        self.click_pos = (0, 0)
        self.recording_click = False
        self.hold_mode = False
        self.hold_duration = 0.1 # Default hold duration in seconds.
        self.trigger_key_text = tk.StringVar(value=f"Current trigger key: {self.trigger_key}")
        
        # Default interval values.
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.milliseconds = 100

        self.config_file = os.path.join(self.config_path, "autoclicker_config.json")
        
        self.setup_gui()
        self.load_config()
        self.setup_keyboard_listener()

    def get_config_path(self):
        if os.name == "nt": base_dir = os.getenv("APPDATA", os.path.expanduser("~"))
        else: base_dir = os.path.expanduser("~/.config")
        config_dir = os.path.join(base_dir, "FJRG2007_projects_data", "SmartAutoClicker")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
        
    def setup_gui(self):
        # Report button.
        report_frame = ttk.Frame(self.root)
        report_frame.pack(fill="x", padx=10, pady=5)
        def open_error_report():
            import webbrowser
            webbrowser.open("https://github.com/FJRG2007/smart-auto-clicker/issues/new")
        try:
            report_icon_path = os.path.join(self.config_path, "report.png")
            if not os.path.exists(report_icon_path):
                response = requests.get("https://raw.githubusercontent.com/FJRG2007/smart-auto-clicker/refs/heads/main/assets/report.png")
                if response.status_code == 200:
                    with open(report_icon_path, "wb") as icon_file:
                        icon_file.write(response.content)
            max_width, max_height = 12, 12
            image = Image.open(report_icon_path)
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            report_icon = ImageTk.PhotoImage(image)
            button_frame = ttk.Frame(report_frame)
            report_button = ttk.Button(report_frame, text="Report Error", image=report_icon, compound="left", command=open_error_report)
            report_button.image = report_icon
            report_button.pack(anchor="w")
        except Exception as e:
            print(f"Error loading icon: {e}")
            report_button = ttk.Button(report_frame, text="Report Error", command=open_error_report)
        report_button.pack(anchor="w")

        # Trigger key settings.
        trigger_frame = ttk.LabelFrame(self.root, text="Trigger Key Settings", padding=10)
        trigger_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(trigger_frame, textvariable=self.trigger_key_text).pack()
        self.trigger_button = ttk.Button(trigger_frame, text="Change trigger key", command=self.record_trigger_key)
        self.trigger_button.pack()
        
        # Interval settings.
        interval_frame = ttk.LabelFrame(self.root, text="Interval Settings", padding=10)
        interval_frame.pack(fill="x", padx=10, pady=5)
        
        time_frame = ttk.Frame(interval_frame)
        time_frame.pack(fill="x", padx=5, pady=5)
        
        # Hours.
        hours_frame = ttk.Frame(time_frame)
        hours_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(hours_frame, text="Hours:").pack()
        self.hours_entry = ttk.Entry(hours_frame, width=5)
        self.hours_entry.insert(0, "0")
        self.hours_entry.pack()
        
        # Minutes.
        minutes_frame = ttk.Frame(time_frame)
        minutes_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(minutes_frame, text="Minutes:").pack()
        self.minutes_entry = ttk.Entry(minutes_frame, width=5)
        self.minutes_entry.insert(0, "0")
        self.minutes_entry.pack()
        
        # Seconds.
        seconds_frame = ttk.Frame(time_frame)
        seconds_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(seconds_frame, text="Seconds:").pack()
        self.seconds_entry = ttk.Entry(seconds_frame, width=5)
        self.seconds_entry.insert(0, "0")
        self.seconds_entry.pack()
        
        # Milliseconds.
        ms_frame = ttk.Frame(time_frame)
        ms_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(ms_frame, text="Milliseconds:").pack()
        self.ms_entry = ttk.Entry(ms_frame, width=5)
        self.ms_entry.insert(0, "100")
        self.ms_entry.pack()
        
        # Click mode settings.
        click_mode_frame = ttk.LabelFrame(self.root, text="Click Mode Settings", padding=10)
        click_mode_frame.pack(fill="x", padx=10, pady=5)
        
        self.mode_var = tk.BooleanVar(value=False)
        ttk.Radiobutton(click_mode_frame, text="Single Click", variable=self.mode_var, value=False, command=self.toggle_mode).pack()
        ttk.Radiobutton(click_mode_frame, text="Hold Button", variable=self.mode_var, value=True, command=self.toggle_mode).pack()
        
        self.hold_frame = ttk.Frame(click_mode_frame)
        ttk.Label(self.hold_frame, text="Hold Duration (seconds):").pack(side=tk.LEFT, padx=5)
        self.hold_entry = ttk.Entry(self.hold_frame, width=8)
        self.hold_entry.insert(0, "0.1")
        self.hold_entry.pack(side=tk.LEFT, padx=5)
        
        # Button settings.
        button_frame = ttk.LabelFrame(self.root, text="Button Settings", padding=10)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(button_frame, text="Click Key/Button:").pack()
        self.click_key_button = ttk.Button(button_frame, text="Click to set button", command=self.record_click_key)
        self.click_key_button.pack()
        
        # Mouse buttons frame.
        mouse_buttons_frame = ttk.Frame(button_frame)
        mouse_buttons_frame.pack(pady=5)
        
        ttk.Button(mouse_buttons_frame, text="Left Click", command=lambda: self.set_mouse_button("left")).pack(side=tk.LEFT, padx=2)
        ttk.Button(mouse_buttons_frame, text="Right Click", command=lambda: self.set_mouse_button("right")).pack(side=tk.LEFT, padx=2)
        ttk.Button(mouse_buttons_frame, text="Middle Click", command=lambda: self.set_mouse_button("middle")).pack(side=tk.LEFT, padx=2)
        
        # Position settings.
        position_frame = ttk.LabelFrame(self.root, text="Position Settings", padding=10)
        position_frame.pack(fill="x", padx=10, pady=5)
        
        self.pos_var = tk.BooleanVar(value=True)
        ttk.Radiobutton(position_frame, text="Use cursor position", variable=self.pos_var, value=True, command=self.toggle_position).pack()
        ttk.Radiobutton(position_frame, text="Use fixed position", variable=self.pos_var, value=False, command=self.toggle_position).pack()
        
        self.position_frame = ttk.Frame(position_frame)
        self.position_frame.pack()
        self.position_label = ttk.Label(self.position_frame, text="Current: (0, 0)")
        self.position_label.pack()
        self.set_position_button = ttk.Button(self.position_frame, text="Set Position", command=self.set_position)
        self.set_position_button.pack()
        
        # Status.
        status_frame = ttk.LabelFrame(self.root, text="Status", padding=10)
        status_frame.pack(fill="x", padx=10, pady=5)

        self.status_label = ttk.Label(status_frame, text="Status: Stopped")
        self.status_label.pack()

        self.trigger_label = ttk.Label(status_frame, text=f"Press ({self.trigger_key}) to start/stop")
        self.trigger_label.pack()

        self.start_stop_button = ttk.Button(status_frame, text="Start", command=self.toggle_clicking)
        self.start_stop_button.pack()

    def toggle_mode(self):
        self.hold_mode = self.mode_var.get()
        if self.hold_mode: self.hold_frame.pack()
        else: self.hold_frame.pack_forget()

    def get_interval(self):
        try:
            hours = int(self.hours_entry.get())
            minutes = int(self.minutes_entry.get())
            seconds = int(self.seconds_entry.get())
            milliseconds = int(self.ms_entry.get())
            total_seconds = (hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000)
            if total_seconds < 0.1:
                messagebox.showwarning("Warning", "Total interval must be at least 0.1 seconds")
                return None  
            return total_seconds
        except ValueError:
            messagebox.showerror("Error", "Invalid time values")
            return None

    def record_trigger_key(self):
        if not self.recording_click:
            self.recording_click = True
            self.trigger_button.config(text="Press F1-F12...")
            def on_key(event):
                if event.name.upper().startswith("F"):
                    try:
                        key_num = int(event.name[1:])
                        if 1 <= key_num <= 12:
                            self.trigger_key = event.name.upper()
                            self.trigger_button.config(text="Change trigger key")
                            self.trigger_key_text.set(f"Current trigger key: {self.trigger_key}")
                            self.trigger_label.config(text=f"Press ({self.trigger_key}) to start/stop")
                            self.recording_click = False
                            self.save_config()
                            unhook_all()
                            self.setup_keyboard_listener()
                    except ValueError: pass
            hook(on_key)

    def set_mouse_button(self, button):
        self.click_key = button
        self.click_key_button.config(text=f"Current: {button} mouse button")
        
    def record_click_key(self):
        if not self.recording_click:
            self.recording_click = True
            self.click_key_button.config(text="Press any key...")
            def on_key(event):
                if event.name.upper() != self.trigger_key:
                    self.click_key = event.name
                    self.click_key_button.config(text=f"Current: {event.name}")
                    self.recording_click = False
                    unhook_all()
                    self.setup_keyboard_listener()
            hook(on_key)
        
    def toggle_position(self):
        self.use_current_pos = self.pos_var.get()
        if self.use_current_pos: self.position_frame.pack_forget()
        else: self.position_frame.pack()
            
    def set_position(self):
        self.root.iconify() # Minimize window.
        time.sleep(2) # Give time to position cursor.
        self.click_pos = mouse.get_position()
        self.position_label.config(text=f"Current: {self.click_pos}")
        self.root.deiconify() # Restore window.
        
    def setup_keyboard_listener(self):
        keyboard.on_press_key(self.trigger_key, lambda e: self.start_stop_listener(e), suppress=True)

    def start_stop_listener(self, event):
        if not self.recording_click: self.toggle_clicking()
        
    def toggle_clicking(self):
        if not self.is_running:
            interval = self.get_interval()
            if interval is None: return
            self.is_running = True
            self.status_label.config(text="Status: Running")
            self.click_thread = Thread(target=self.clicking_loop)
            self.click_thread.daemon = True
            self.click_thread.start()
        else:
            self.is_running = False
            self.status_label.config(text="Status: Stopped")
        self.start_stop_button.config(text="Stop" if self.is_running else "Start")
            
    def clicking_loop(self):
        while self.is_running:
            if not self.use_current_pos: mouse.move(self.click_pos[0], self.click_pos[1])
            
            if self.click_key in ["left", "right", "middle"]:
                if self.hold_mode:
                    mouse.press(self.click_key)
                    time.sleep(float(self.hold_entry.get()))
                    mouse.release(self.click_key)
                else: mouse.click(self.click_key)
            else:
                if self.hold_mode:
                    keyboard.press(self.click_key)
                    time.sleep(float(self.hold_entry.get()))
                    keyboard.release(self.click_key)
                else: keyboard.press_and_release(self.click_key)
            interval = self.get_interval()
            if interval is None:
                self.is_running = False
                self.status_label.config(text="Status: Stopped")
                return
            time.sleep(interval)
            
    def save_config(self):
        config = {
            "hours": self.hours_entry.get(),
            "minutes": self.minutes_entry.get(),
            "seconds": self.seconds_entry.get(),
            "milliseconds": self.ms_entry.get(),
            "click_key": self.click_key,
            "use_current_pos": self.use_current_pos,
            "click_pos": self.click_pos,
            "trigger_key": self.trigger_key,
            "hold_mode": self.hold_mode,
            "hold_duration": self.hold_entry.get(),
            "window_x": self.root.winfo_x(),
            "window_y": self.root.winfo_y()
        }
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f)
        except Exception as e: messagebox.showerror("Error", f"Error saving configuration:\n{e}")
            
    def load_config(self):
        default_config = {
            "hours": "0",
            "minutes": "0",
            "seconds": "0",
            "milliseconds": "100",
            "click_key": "left",
            "use_current_pos": True,
            "click_pos": [0, 0],
            "trigger_key": "F6",
            "hold_mode": False,
            "hold_duration": "0.1",
            "window_x": 100,
            "window_y": 100
        }
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
            except Exception as e:
                messagebox.showwarning("Warning", f"Error loading configuration. Using defaults.\n{e}")
                config = default_config
        else: config = default_config
        try:
            # Load time values.
            self.hours_entry.delete(0, tk.END)
            self.hours_entry.insert(0, config.get("hours", "0"))
            self.minutes_entry.delete(0, tk.END)
            self.minutes_entry.insert(0, config.get("minutes", "0"))
            self.seconds_entry.delete(0, tk.END)
            self.seconds_entry.insert(0, config.get("seconds", "0"))
            self.ms_entry.delete(0, tk.END)
            self.ms_entry.insert(0, config.get("milliseconds", "100"))
                
            # Load other settings.
            self.click_key = config.get("click_key", "left")
            self.click_key_button.config(text=f"Current: {self.click_key}")
            self.use_current_pos = config.get("use_current_pos", True)
            self.click_pos = tuple(config.get("click_pos", (0, 0)))
            self.trigger_key = config.get("trigger_key", "F6")
            self.trigger_label.config(text=f"Press {self.trigger_key} to start/stop")
            self.hold_mode = config.get("hold_mode", False)
            self.setup_keyboard_listener()
                
            # Update GUI.
            self.click_key_button.config(text=f"Current: {self.click_key}")
            self.pos_var.set(self.use_current_pos)
            self.position_label.config(text=f"Current: {self.click_pos}")
            self.trigger_label.config(text=f"Press {self.trigger_key} to start/stop")
            self.mode_var.set(self.hold_mode)
            self.hold_entry.delete(0, tk.END)
            self.hold_entry.insert(0, config.get("hold_duration", "0.1"))
                
            self.toggle_position()
            self.toggle_mode()

            window_x = config.get("window_x", 100)
            window_y = config.get("window_y", 100)
            self.root.geometry(f"+{window_x}+{window_y}")
            self.root.deiconify()
        except: pass
                
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.main
                
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        self.is_running = False
        keyboard.unhook_all()
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    app = AutoClicker()
    app.run()