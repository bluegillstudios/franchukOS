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
import threading
import time
from config.manager import load_config
from core.thememanage import apply_theme
import random

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
        self.current_wallpaper = None
        self.current_theme = None
        self.config = load_config()
        if not isinstance(self.config, dict):
            self.config = {}
        self.set_wallpaper(self.config.get("wallpaper", "assets/backgrounds/wallpaper.jpg"))
        apply_theme(self, self.config.get("theme", "light"))  # Apply theme at startup
        self.poll_wallpaper_config()
        self.setup_ui()

        self.screensaver_timeout = int(self.config.get("screensaver_timeout", 300))  # seconds
        self.screensaver_active = False
        self.last_activity = time.time()
        self.screensaver_window = None
        self.bind_all("<Any-KeyPress>", self.reset_screensaver_timer)
        self.bind_all("<Any-Button>", self.reset_screensaver_timer)
        self.bind_all("<Motion>", self.reset_screensaver_timer)
        self.start_screensaver_timer()

    def poll_wallpaper_config(self):
        def watcher():
            while True:
                try:
                    config = load_config()
                    if not isinstance(config, dict):
                        config = {}
                    # Wallpaper update
                    wallpaper = config.get("wallpaper", "assets/backgrounds/wallpaper.jpg")
                    if wallpaper != self.current_wallpaper:
                        self.current_wallpaper = wallpaper
                        if wallpaper.startswith("#") or wallpaper in ["black", "white", "gray", "grey"]:
                            self.configure(bg=wallpaper)
                            if self.wallpaper_label:
                                self.wallpaper_label.destroy()
                                self.wallpaper_label = None
                        else:
                            self.set_wallpaper(wallpaper)
                    # Theme update
                    theme = config.get("theme", "light")
                    if theme != self.current_theme:
                        self.current_theme = theme
                        apply_theme(self, theme)
                    time.sleep(2)
                except Exception as e:
                    print(f"Wallpaper/theme watcher error: {e}")
                    time.sleep(2)
        threading.Thread(target=watcher, daemon=True).start()

    def set_wallpaper(self, path):
        try:
            wallpaper_img = Image.open(path)
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            wallpaper_img = wallpaper_img.resize((screen_width, screen_height), Image.LANCZOS)
            self.wallpaper_photo = ImageTk.PhotoImage(wallpaper_img)
            if self.wallpaper_label:
                self.wallpaper_label.config(image=self.wallpaper_photo)
            else:
                self.wallpaper_label = tk.Label(self, image=self.wallpaper_photo, bd=0)
                self.wallpaper_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.wallpaper_label.lower()  # <-- This line ensures wallpaper is always at the back
        except Exception as e:
            print(f"Could not load wallpaper from {path}: {e}")
            self.configure(bg="black")
            if self.wallpaper_label:
                self.wallpaper_label.destroy()
                self.wallpaper_label = None

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

    def reset_screensaver_timer(self, event=None):
        self.last_activity = time.time()
        if self.screensaver_active:
            self.deactivate_screensaver()

    def start_screensaver_timer(self):
        def check():
            while True:
                if not self.screensaver_active and (time.time() - self.last_activity > self.screensaver_timeout):
                    self.activate_screensaver()
                time.sleep(2)
        threading.Thread(target=check, daemon=True).start()
        def activate_screensaver(self):
            self.screensaver_active = True
            self.screensaver_window = tk.Toplevel(self)
            self.screensaver_window.attributes("-fullscreen", True)
            self.screensaver_window.configure(bg="black")
            self.screensaver_window.lift()
            self.screensaver_window.focus_set()
            self.screensaver_window.bind("<Any-KeyPress>", self.reset_screensaver_timer)
            self.screensaver_window.bind("<Any-Button>", self.reset_screensaver_timer)
            self.screensaver_window.bind("<Motion>", self.reset_screensaver_timer)

            label = tk.Label(
                self.screensaver_window,
                text="Franchuk is waiting....",
                fg="white",
                bg="black",
                font=("Segoe UI", 48)
            )
            label.place(x=0, y=0)

            def move_label():
                if not self.screensaver_active or not self.screensaver_window:
                    return
                sw = self.screensaver_window.winfo_width()
                sh = self.screensaver_window.winfo_height()
                lw = label.winfo_reqwidth()
                lh = label.winfo_reqheight()
                x = random.randint(0, max(0, sw - lw))
                y = random.randint(0, max(0, sh - lh))
                label.place(x=x, y=y)
                self.screensaver_window.after(1200, move_label)

            # Wait for window to update so we get correct dimensions
            self.screensaver_window.after(100, move_label)

    def deactivate_screensaver(self, event=None):
        if self.screensaver_window:
            self.screensaver_window.destroy()
            self.screensaver_window = None
        self.screensaver_active = False
        self.last_activity = time.time()

if __name__ == "__main__":
    desktop = Desktop()
    desktop.mainloop()
