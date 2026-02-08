from threading import Thread
from PIL import Image, ImageTk
from src.memory import MemoryManager
from src.windows import WindowsManager
from tkinter import ttk, messagebox
from keyboard import hook, unhook_all
from src.clickers.simulating_game import GameSimulator
from src.clickers.antidetection_bypass import AntiDetectionBypass, BypassProfile
from src.clickers.native_input import NativeInput, InputMethod, get_native_input
import os, json, time, mouse, random, tkinter as tk, keyboard, src.lib.globals as globals

class AutoClicker:
    def __init__(self):
        self.root = tk.Tk()
        self.startup_mode = MemoryManager.get("startup_mode", "normal")
        if self.startup_mode == "minimized":
            self.root.withdraw()
            self.root.after(0, lambda: self.root.iconify())
        elif self.startup_mode == "tray":
            self.root.withdraw()
            self.setup_system_tray()
        elif MemoryManager.get("use_current_pos", True): 
            self.root.withdraw()
            self.root.geometry(f"+{MemoryManager.get("window_x", 100)}+{MemoryManager.get("window_y", 100)}")
            self.root.deiconify()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.title("Smart Auto Clicker - FJRG2007")
        self.root.geometry("400x920")
        self.root.resizable(False, False)
        globals.app_config_file_path = os.path.join(globals.app_config_path, "autoclicker_config.json")
        self.windows_manager = WindowsManager(self.root)

        # Icon.
        self.root.iconbitmap(globals.app_icon_path)
        
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

        # Anti-detection bypass system.
        self.bypass_enabled = False
        self.bypass_profile = BypassProfile.MODERATE
        self.bypass_system = AntiDetectionBypass(self.bypass_profile)

        # Native input system for game compatibility.
        self.use_native_input = False
        self.native_input_method = InputMethod.AUTO
        self.native_input = get_native_input()
        
        # Default interval values.
        self.hours = 0
        self.minutes = 0
        self.seconds = 0
        self.milliseconds = 100
        
        self.setup_gui()
        self.load_config()
        self.setup_keyboard_listener()

    def setup_gui(self):
        # Report button.
        menu_frame = ttk.Frame(self.root)
        menu_frame.pack(fill="x", padx=10, pady=5)

        def open_error_report():
            import webbrowser
            webbrowser.open("https://github.com/FJRG2007/smart-auto-clicker/issues/new")
        try:
            image = Image.open(globals.app_report_icon_path)
            report_icon = ImageTk.PhotoImage(image)
            report_button = ttk.Button(menu_frame, text="Report Error", image=report_icon, compound="left", command=open_error_report)
            report_button.image = report_icon
        except Exception as e:
            print(f"Error loading icon: {e}")
            report_button = ttk.Button(menu_frame, text="Report Error", command=open_error_report)

        # Simulate game button.
        simulate_button = ttk.Button(menu_frame, text="Simulate Playing")
        self.game_simulator = GameSimulator(self.root, simulate_button)

        # Settings button.
        settings_button = ttk.Button(menu_frame, text="Open Settings", command=self.windows_manager.open_config_window)

        report_button.grid(row=0, column=0, padx=5)
        settings_button.grid(row=0, column=1, padx=5)
        simulate_button.grid(row=0, column=2, padx=5)

        menu_frame.grid_columnconfigure(0, weight=1)
        menu_frame.grid_columnconfigure(1, weight=1)
        menu_frame.grid_columnconfigure(2, weight=1)

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
        
        # Hold duration section.
        self.hold_frame = ttk.Frame(click_mode_frame)
        ttk.Label(self.hold_frame, text="Hold Duration (seconds):").pack(side=tk.LEFT, padx=5)
        # Entry field for hold duration.
        self.hold_entry = ttk.Entry(self.hold_frame, width=8)
        self.hold_entry.insert(0, "0.1")
        self.hold_entry.pack(side=tk.LEFT, padx=5)

        # Add explanatory note.
        self.hold_note = ttk.Label(self.hold_frame, text="Set to 0 for infinite hold.", font=("Arial", 8), foreground="gray")
        self.hold_note.pack(side=tk.LEFT, padx=5)

        # Anti-Detection Bypass Settings.
        bypass_frame = ttk.LabelFrame(self.root, text="Anti-Detection Bypass", padding=10)
        bypass_frame.pack(fill="x", padx=10, pady=5)

        # Enable/Disable bypass.
        self.bypass_var = tk.BooleanVar(value=False)
        bypass_toggle_frame = ttk.Frame(bypass_frame)
        bypass_toggle_frame.pack(fill="x")

        self.bypass_checkbox = ttk.Checkbutton(
            bypass_toggle_frame,
            text="Enable Anti-Detection Mode",
            variable=self.bypass_var,
            command=self.toggle_bypass
        )
        self.bypass_checkbox.pack(side=tk.LEFT)

        # Bypass profile selector.
        self.bypass_profile_frame = ttk.Frame(bypass_frame)

        ttk.Label(self.bypass_profile_frame, text="Profile:").pack(side=tk.LEFT, padx=5)

        self.profile_var = tk.StringVar(value="moderate")
        profile_options = [
            ("Light", "light"),
            ("Moderate", "moderate"),
            ("Aggressive", "aggressive"),
            ("Adaptive", "adaptive")
        ]

        for text, value in profile_options:
            ttk.Radiobutton(
                self.bypass_profile_frame,
                text=text,
                variable=self.profile_var,
                value=value,
                command=self.change_bypass_profile
            ).pack(side=tk.LEFT, padx=3)

        # Bypass info label.
        self.bypass_info_frame = ttk.Frame(bypass_frame)
        self.bypass_status_label = ttk.Label(
            self.bypass_info_frame,
            text="Humanizes click patterns to evade anti-cheat detection",
            font=("Arial", 8),
            foreground="gray"
        )
        self.bypass_status_label.pack()

        # Stats display (shows during runtime).
        self.bypass_stats_label = ttk.Label(
            self.bypass_info_frame,
            text="",
            font=("Arial", 8),
            foreground="blue"
        )
        self.bypass_stats_label.pack()

        # Native Input Settings (Game Compatibility).
        native_frame = ttk.LabelFrame(self.root, text="Game Compatibility Mode", padding=10)
        native_frame.pack(fill="x", padx=10, pady=5)

        # Enable native input.
        self.native_var = tk.BooleanVar(value=False)
        native_toggle_frame = ttk.Frame(native_frame)
        native_toggle_frame.pack(fill="x")

        self.native_checkbox = ttk.Checkbutton(
            native_toggle_frame,
            text="Enable Native Input (for games)",
            variable=self.native_var,
            command=self.toggle_native_input
        )
        self.native_checkbox.pack(side=tk.LEFT)

        # Input method selector.
        self.native_method_frame = ttk.Frame(native_frame)

        ttk.Label(self.native_method_frame, text="Method:").pack(side=tk.LEFT, padx=5)

        self.input_method_var = tk.StringVar(value="auto")
        input_methods = [
            ("Auto", "auto"),
            ("SendInput", "sendinput"),
            ("Legacy", "mouse_event"),
        ]

        for text, value in input_methods:
            ttk.Radiobutton(
                self.native_method_frame,
                text=text,
                variable=self.input_method_var,
                value=value,
                command=self.change_input_method
            ).pack(side=tk.LEFT, padx=3)

        # Native input info.
        self.native_info_frame = ttk.Frame(native_frame)

        # Check if interception is available.
        interception_status = "Available" if self.native_input.is_interception_available() else "Not installed"
        self.native_status_label = ttk.Label(
            self.native_info_frame,
            text=f"Low-level input for anti-cheat games | Interception: {interception_status}",
            font=("Arial", 8),
            foreground="gray"
        )
        self.native_status_label.pack()

        self.native_method_label = ttk.Label(
            self.native_info_frame,
            text=f"Active: {self.native_input.get_method_name()}",
            font=("Arial", 8),
            foreground="green"
        )
        self.native_method_label.pack()

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

    def toggle_bypass(self):
        """Toggle anti-detection bypass mode."""
        self.bypass_enabled = self.bypass_var.get()
        if self.bypass_enabled:
            self.bypass_profile_frame.pack(fill="x", pady=5)
            self.bypass_info_frame.pack(fill="x")
            self.bypass_system.reset_session()
            profile_descriptions = {
                "light": "Light: Minimal variation, faster but less safe",
                "moderate": "Moderate: Balanced speed and safety",
                "aggressive": "Aggressive: Maximum humanization, slower but safest",
                "adaptive": "Adaptive: Auto-adjusts based on detection risk"
            }
            desc = profile_descriptions.get(self.profile_var.get(), "")
            self.bypass_status_label.config(text=desc)
        else:
            self.bypass_profile_frame.pack_forget()
            self.bypass_info_frame.pack_forget()
            self.bypass_stats_label.config(text="")

    def change_bypass_profile(self):
        """Change the bypass profile."""
        profile_map = {
            "light": BypassProfile.LIGHT,
            "moderate": BypassProfile.MODERATE,
            "aggressive": BypassProfile.AGGRESSIVE,
            "adaptive": BypassProfile.ADAPTIVE
        }
        profile_name = self.profile_var.get()
        self.bypass_profile = profile_map.get(profile_name, BypassProfile.MODERATE)
        self.bypass_system = AntiDetectionBypass(self.bypass_profile)

        profile_descriptions = {
            "light": "Light: Minimal variation, faster but less safe",
            "moderate": "Moderate: Balanced speed and safety",
            "aggressive": "Aggressive: Maximum humanization, slower but safest",
            "adaptive": "Adaptive: Auto-adjusts based on detection risk"
        }
        desc = profile_descriptions.get(profile_name, "")
        self.bypass_status_label.config(text=desc)

    def update_bypass_stats(self):
        """Update bypass statistics display."""
        if self.bypass_enabled and self.is_running:
            stats = self.bypass_system.get_stats()
            risk_level = "Low" if stats['detection_risk'] < 0.3 else "Medium" if stats['detection_risk'] < 0.6 else "High"
            stats_text = f"Clicks: {stats['click_count']} | Fatigue: {stats['fatigue_level']:.1%} | Risk: {risk_level}"
            self.bypass_stats_label.config(text=stats_text)
            if self.is_running:
                self.root.after(1000, self.update_bypass_stats)
        else:
            self.bypass_stats_label.config(text="")

    def toggle_native_input(self):
        """Toggle native input mode for game compatibility."""
        self.use_native_input = self.native_var.get()
        if self.use_native_input:
            self.native_method_frame.pack(fill="x", pady=5)
            self.native_info_frame.pack(fill="x")
            self.native_method_label.config(text=f"Active: {self.native_input.get_method_name()}")
        else:
            self.native_method_frame.pack_forget()
            self.native_info_frame.pack_forget()

    def change_input_method(self):
        """Change the native input method."""
        method_map = {
            "auto": InputMethod.AUTO,
            "sendinput": InputMethod.SENDINPUT,
            "mouse_event": InputMethod.MOUSE_EVENT,
        }
        method_name = self.input_method_var.get()
        method = method_map.get(method_name, InputMethod.AUTO)

        # Recreate native input with new method.
        self.native_input = NativeInput(method)
        self.native_method_label.config(text=f"Active: {self.native_input.get_method_name()}")

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
            # Reset bypass system for new session.
            if self.bypass_enabled:
                self.bypass_system.reset_session()
                self.update_bypass_stats()
            self.click_thread = Thread(target=self.clicking_loop)
            self.click_thread.daemon = True
            self.click_thread.start()
        else:
            self.is_running = False
            self.status_label.config(text="Status: Stopped")
            self.bypass_stats_label.config(text="")
        self.start_stop_button.config(text="Stop" if self.is_running else "Start")

    def human_delay(self, base: float, variation: float = 0.02):
        return max(0, base + random.uniform(-variation, variation))

    def move_mouse_naturally(self, x, y):
        """Move mouse with natural human-like motion."""
        current_x, current_y = mouse.position

        if self.bypass_enabled:
            # Use bypass system for enhanced humanization.
            params = self.bypass_system.get_mouse_movement_params()
            steps = params['steps']
            base_delay = params['delay']
            curve = params['curve']

            # Apply jitter to target position.
            x, y = self.bypass_system.get_mouse_jitter(x, y)

            for i in range(1, steps + 1):
                t = i / steps
                # Apply movement curve for more natural motion.
                t_curved = self.bypass_system.apply_movement_curve(t, curve)

                new_x = current_x + (x - current_x) * t_curved
                new_y = current_y + (y - current_y) * t_curved

                # Add micro-jitter during movement.
                if random.random() < 0.2:
                    new_x += random.gauss(0, 1)
                    new_y += random.gauss(0, 1)

                mouse.position = (int(new_x), int(new_y))

                # Variable delay with gaussian distribution.
                delay = self.bypass_system.gaussian_variation(base_delay)
                time.sleep(max(0.001, delay))
        else:
            # Original simple movement.
            steps = random.randint(5, 15)
            for i in range(1, steps + 1):
                new_x = current_x + (x - current_x) * i / steps
                new_y = current_y + (y - current_y) * i / steps
                mouse.position = (int(new_x), int(new_y))
                time.sleep(self.human_delay(0.005, 0.003))

    def clicking_loop(self):
        """Main clicking loop with optional anti-detection bypass and native input."""
        # Handle infinite hold mode.
        if self.hold_mode and float(self.hold_entry.get()) == 0:
            if self.click_key in ["left", "right", "middle"]:
                if self.use_native_input:
                    self.native_input.mouse_down(self.click_key)
                else:
                    mouse.press(self.click_key)
            else:
                if self.use_native_input:
                    self.native_input.key_down(self.click_key)
                else:
                    keyboard.press(self.click_key)
            while self.is_running:
                time.sleep(0.1)
            if self.click_key in ["left", "right", "middle"]:
                if self.use_native_input:
                    self.native_input.mouse_up(self.click_key)
                else:
                    mouse.release(self.click_key)
            else:
                if self.use_native_input:
                    self.native_input.key_up(self.click_key)
                else:
                    keyboard.release(self.click_key)
            return

        while self.is_running:
            # Move mouse if using fixed position.
            if not self.use_current_pos:
                self.move_mouse_naturally(*self.click_pos)

            hold_time = float(self.hold_entry.get())

            # Determine hold duration.
            if self.bypass_enabled and self.hold_mode:
                actual_hold_time = self.bypass_system.get_hold_duration(hold_time)
            else:
                actual_hold_time = self.human_delay(hold_time)

            # Execute click or hold using native input or standard library.
            if self.click_key in ["left", "right", "middle"]:
                if self.hold_mode:
                    if self.use_native_input:
                        self.native_input.mouse_down(self.click_key)
                        time.sleep(actual_hold_time)
                        self.native_input.mouse_up(self.click_key)
                    else:
                        mouse.press(self.click_key)
                        time.sleep(actual_hold_time)
                        mouse.release(self.click_key)
                else:
                    if self.use_native_input:
                        self.native_input.click(self.click_key)
                    else:
                        mouse.click(self.click_key)
            else:
                if self.hold_mode:
                    if self.use_native_input:
                        self.native_input.key_down(self.click_key)
                        time.sleep(actual_hold_time)
                        self.native_input.key_up(self.click_key)
                    else:
                        keyboard.press(self.click_key)
                        time.sleep(actual_hold_time)
                        keyboard.release(self.click_key)
                else:
                    if self.use_native_input:
                        self.native_input.key_press(self.click_key)
                    else:
                        keyboard.press(self.click_key)
                        keyboard.release(self.click_key)

            # Get base interval.
            interval = self.get_interval()
            if interval is None:
                self.is_running = False
                self.status_label.config(text="Status: Stopped")
                return

            # Calculate delay with or without bypass.
            if self.bypass_enabled:
                # Use advanced humanization.
                delay = self.bypass_system.get_humanized_delay(interval)
                # Adapt profile if using adaptive mode.
                self.bypass_system.adapt_profile()
            else:
                # Use simple variation.
                delay = self.human_delay(interval, 0.03)

            time.sleep(delay)  
            
    def save_config(self):
        with open(globals.app_config_file_path, "r") as f:
            current_config = json.load(f)
        new_config = {
            "hours": self.hours_entry.get(),
            "minutes": self.minutes_entry.get(),
            "seconds": self.seconds_entry.get(),
            "milliseconds": self.ms_entry.get(),
            "click_key": self.click_key,
            "use_current_pos": current_config["use_current_pos"],
            "startup_mode": current_config["startup_mode"],
            "exec_on_startup": current_config["exec_on_startup"],
            "click_pos": self.click_pos,
            "trigger_key": self.trigger_key,
            "hold_mode": self.hold_mode,
            "hold_duration": self.hold_entry.get(),
            "window_x": self.root.winfo_x(),
            "window_y": self.root.winfo_y(),
            "bypass_enabled": self.bypass_enabled,
            "bypass_profile": self.profile_var.get(),
            "native_input_enabled": self.use_native_input,
            "native_input_method": self.input_method_var.get()
        }
        try:
            with open(globals.app_config_file_path, "w") as f:
                json.dump(new_config, f)
            MemoryManager.set("window_x", new_config["window_x"])
            MemoryManager.set("window_y", new_config["window_y"])
            MemoryManager.save_memory()
        except Exception as e: messagebox.showerror("Error", f"Error saving configuration:\n{e}")
            
    def load_config(self, force_create_file=True):
        default_config = {
            "hours": "0",
            "minutes": "0",
            "seconds": "0",
            "milliseconds": "100",
            "click_key": "left",
            "use_current_pos": True,
            "startup_mode": "normal",
            "exec_on_startup": False,
            "click_pos": [0, 0],
            "trigger_key": "F6",
            "hold_mode": False,
            "hold_duration": "0.1",
            "window_x": 100,
            "window_y": 100,
            "bypass_enabled": False,
            "bypass_profile": "moderate",
            "native_input_enabled": False,
            "native_input_method": "auto"
        }
        if os.path.exists(globals.app_config_file_path):
            try:
                with open(globals.app_config_file_path, "r") as f:
                    config = json.load(f)
            except Exception as e:
                messagebox.showwarning("Warning", f"Error loading configuration. Using defaults.\n{e}")
                config = default_config
        else: 
            config = default_config
            if force_create_file:
                try:
                    with open(globals.app_config_file_path, "w") as f:
                        json.dump(config, f)
                except Exception as e: messagebox.showerror("Error", f"Error creating configuration file:\n{e}")
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

            # Load bypass settings.
            self.bypass_enabled = config.get("bypass_enabled", False)
            self.bypass_var.set(self.bypass_enabled)
            bypass_profile = config.get("bypass_profile", "moderate")
            self.profile_var.set(bypass_profile)
            self.change_bypass_profile()
            self.toggle_bypass()

            # Load native input settings.
            self.use_native_input = config.get("native_input_enabled", False)
            self.native_var.set(self.use_native_input)
            native_method = config.get("native_input_method", "auto")
            self.input_method_var.set(native_method)
            self.change_input_method()
            self.toggle_native_input()
        except: pass

    def setup_system_tray(self):
        from PIL import Image
        from pystray import Icon, MenuItem, Menu
        image = image = Image.open(globals.app_icon_path)
        def show_window(icon, item):
            self.root.deiconify()
            icon.stop()
        def exit_application(icon, item):
            self.root.destroy()
            icon.stop()
        menu = Menu(
            MenuItem("Open", show_window),
            MenuItem("Exit", exit_application)
        )
        self.tray_icon = Icon("Smart Auto Clicker", image, "Smart Auto Clicker", menu)
        self.tray_icon.run_detached()
                
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        self.is_running = False
        keyboard.unhook_all()
        self.native_input.cleanup()
        self.save_config()
        self.root.destroy()

def main():
    app = AutoClicker()
    app.run()