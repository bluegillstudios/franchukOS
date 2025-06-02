# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from PIL import Image, ImageTk
from Graphics.taskbar import Taskbar, WindowManager
from Graphics.utils import set_background_image, set_background_color
from Applications.file_explorer import FileExplorer
from Applications.terminal import Terminal
from Applications.settings import SettingsApp
from Applications.clock import ClockApp
from Applications.insider import Insider
from Applications.outsider import Outsider
from Applications.franny import FrannyBrowser
from Applications.franpaint import Franpaint
from Applications.games.snake import snake_game as SnakeGame
from Applications.games.spi import SpaceInvaders
from Applications.games.aloha import AlohaGameGUI as Aloha

class Desktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FranchukOS Desktop")
        self.geometry("1200x800")  # Starting size for the window
        self.resizable(True, True)  # Allow resizing the window

        # Initialize window manager here instead of passing to taskbar
        self.window_manager = WindowManager(self)

        # Only pass the window to Taskbar if that's the expected argument
        self.taskbar = Taskbar(self)

        self.icons = []
        self.icon_images = [] 
        self.wallpaper_label = None
        self.set_wallpaper("assets/backgrounds/wallpaper.jpg")
        self.setup_ui()

    def set_wallpaper(self, path):
        try:
            wallpaper_img = Image.open(path)
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            wallpaper_img = wallpaper_img.resize((screen_width, screen_height), Image.LANCZOS)
            self.wallpaper_photo = ImageTk.PhotoImage(wallpaper_img)

            self.wallpaper_label = tk.Label(self, image=self.wallpaper_photo)
            self.wallpaper_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Could not load wallpaper from {path}: {e}")
            self.configure(bg="black")

    def setup_ui(self):
        # Place icons on top of wallpaper
        self.icon_container = tk.Frame(self, bg="", bd=0)
        self.icon_container.place(relx=0, rely=0)

        apps = [
            ("Terminal", "assets/icons/apps/terminal.png", Terminal),
            ("File Explorer", "assets/icons/apps/files.png", FileExplorer),
            ("Settings", "assets/icons/apps/settings.png", SettingsApp),
            ("Clock", "assets/icons/apps/clock.png", ClockApp),
            ("Insider", "assets/icons/apps/insider.png", Insider),
            ("Outsider", "assets/icons/apps/viewer.png", Outsider),
            ("Franny", "assets/icons/apps/franny.png", FrannyBrowser),
            ("Snake", "assets/icons/games/snake.jpg", SnakeGame),
            ("Space Invaders", "assets/icons/games/spi.jpg", SpaceInvaders),
            ("Aloha", "assets/icons/games/aloha.jpg", Aloha),
            ("Franpaint", "assets/icons/apps/franpaint.png", Franpaint),
        ]

        for idx, (name, icon_path, app_class) in enumerate(apps):
            self.create_icon(name, icon_path, app_class, row=idx//5, col=idx%5)

        self.taskbar.lift()
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_icon(self, name, icon_path, app_class, row, col):
        try:
            icon_img = Image.open(icon_path).resize((64, 64), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_img)
        except Exception as e:
            print(f"Failed to load icon '{name}' from {icon_path}: {e}")
            return

        icon_frame = tk.Frame(self.icon_container, bg="#000000", bd=0)
        icon_frame.place(x=40 + col * 100, y=40 + row * 100)

        icon_button = tk.Button(
            icon_frame,
            image=icon_photo,
            command=lambda: self.window_manager.launch(app_class),
            bd=0,
            bg="#000000",
            activebackground="#222222"
        )
        icon_button.pack()

        label = tk.Label(icon_frame, text=name, fg="white", bg="#000000", font=("Arial", 10))
        label.pack()

        self.icons.append(icon_frame)
        self.icon_images.append(icon_photo)  

if __name__ == "__main__":
    desktop = Desktop()
    desktop.mainloop()
