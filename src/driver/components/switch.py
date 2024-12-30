import tkinter as tk
from tkinter import ttk
from src.utils.basics import get_resource_path

on_image_path = get_resource_path("assets/switch-on.png")
off_image_path = get_resource_path("assets/switch-off.png")

class Switch(tk.Frame):
    def __init__(self, parent, initial_state=True, command=None, **kwargs):
        super().__init__(parent, **kwargs)

        self.on_image = tk.PhotoImage(file=on_image_path)
        self.off_image = tk.PhotoImage(file=off_image_path)

        self.is_on = initial_state

        self.command = command

        self.label = ttk.Label(self, text="The Switch is On!" if self.is_on else "The Switch is Off!", font=("Helvetica", 12))
        self.label.pack(pady=5)

        self.button = ttk.Button(self, image=self.on_image if self.is_on else self.off_image, command=self.toggle)
        self.button.pack()

    def toggle(self):
        self.is_on = not self.is_on
        self.button.config(image=self.on_image if self.is_on else self.off_image)
        self.label.config(
            text="The Switch is On!" if self.is_on else "The Switch is Off!",
            foreground="green" if self.is_on else "grey",
        )
        if self.command: self.command(self.is_on)
