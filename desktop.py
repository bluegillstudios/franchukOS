# Copyright 2025 the FranchukOS project authors. 
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from gui.taskbar import Taskbar
from gui.utils import set_background_image
from apps.file_explorer import FileExplorer
from apps.terminal import Terminal
from apps.settings import SettingsApp
from gui.taskbar import WindowManager

class Desktop:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FranchukOS")
        self.root.geometry("1024x768")
        self.root.configure(bg="black")
        self.root.overrideredirect(False)  

        set_background_image(self.root, "assets/backgrounds/wallpaper.png")

        self.window_manager = WindowManager(self.root)
        self.taskbar = Taskbar(self.root, self.window_manager)

        self.create_desktop_icons()

    def create_desktop_icons(self):
        self.icon_frame = tk.Frame(self.root, bg="black")
        self.icon_frame.pack(side="top", fill="both", expand=True)

        screen_width = self.root.winfo_width()
        screen_height = self.root.winfo_height()

        icon_spacing = 20
        cols = max(screen_width // 100, 5)
        rows = max(screen_height // 100, 4)

        icon_width = (screen_width - (cols + 1) * icon_spacing) // cols
        icon_height = (screen_height - (rows + 1) * icon_spacing) // rows

        app_info = [
            ("icons/file_explorer_icon.png", "File Explorer", FileExplorer),
            ("icons/terminal_icon.png", "Terminal", Terminal),
            ("icons/settings_icon.png", "Settings", SettingsApp)  
            
        ]

        for i, (icon_path, app_name, app_class) in enumerate(app_info):
            row = i // cols
            col = i % cols

            icon_image = tk.PhotoImage(file=icon_path)
            button = tk.Button(
                self.icon_frame,
                image=icon_image,
                text=app_name,
                compound="top",
                width=icon_width,
                height=icon_height,
                relief="solid",
                borderwidth=2,
                bg="black",
                fg="lime",
                font=("Courier", 10),
                command=lambda app_class=app_class, app_name=app_name: self.launch_app(app_class, app_name)
            )
            button.grid(row=row, column=col, padx=icon_spacing, pady=icon_spacing)
            button.image = icon_image

    def launch_app(self, app_class, app_name):
        self.window_manager.open_window(app_name, app_class)

    def run(self):
        self.root.mainloop()