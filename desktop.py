# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
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
import itertools
import os


class Desktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Desktop")

        # Fullscreen by default now
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.window_manager = WindowManager(self)
        self.taskbar = Taskbar(self)

        self.icons = []
        self.icon_images = [] 
        self.wallpaper_label = None
        self.current_wallpaper = None
        self.current_theme = None
        self.config = load_config()
        if not isinstance(self.config, dict):
            self.config = {}

        # Dynamic wallpaper attributes
        self.wallpaper_frames = None
        self.wallpaper_index = 0
        self.wallpaper_animating = False

        self.set_wallpaper(self.config.get("wallpaper", "Assets/backgrounds/wallpaper.jpg"))
        apply_theme(self, self.config.get("theme", "light"))
        self.poll_wallpaper_config()
        self.setup_ui()

        # Screensaver
        self.screensaver_timeout = int(self.config.get("screensaver_timeout", 300))
        self.screensaver_active = False
        self.last_activity = time.time()
        self.screensaver_window = None
        self.bind_all("<Any-KeyPress>", self.reset_screensaver_timer)
        self.bind_all("<Any-Button>", self.reset_screensaver_timer)
        self.bind_all("<Motion>", self.reset_screensaver_timer)
        self.start_screensaver_timer()

    # Wallpaper shit 
    def poll_wallpaper_config(self):
        def watcher():
            while True:
                try:
                    config = load_config()
                    if not isinstance(config, dict):
                        config = {}
                    wallpaper = config.get("wallpaper", "Assets/backgrounds/wallpaper.jpg")
                    if wallpaper != self.current_wallpaper:
                        self.set_wallpaper(wallpaper)
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
        """Supports static images, animated GIFs, and folder slideshows."""
        try:
            self.current_wallpaper = path
            self.wallpaper_frames = None
            self.wallpaper_animating = False

            if os.path.isdir(path):
                # Slideshow mode
                images = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith((".jpg", ".png"))]
                if not images:
                    raise FileNotFoundError("No valid images in slideshow folder")
                self.wallpaper_frames = itertools.cycle(images)
                self.animate_slideshow()
                return

            img = Image.open(path)

            if getattr(img, "is_animated", False):  
                self.wallpaper_frames = [ImageTk.PhotoImage(frame.resize(
                    (self.winfo_screenwidth(), self.winfo_screenheight()), Image.LANCZOS)) 
                    for frame in ImageSequence.Iterator(img)]
                self.wallpaper_index = 0
                self.wallpaper_animating = True
                if not self.wallpaper_label:
                    self.wallpaper_label = tk.Label(self, bd=0)
                    self.wallpaper_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.animate_wallpaper()
                return

            # Static image
            img = img.resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.LANCZOS)
            self.wallpaper_photo = ImageTk.PhotoImage(img)
            if self.wallpaper_label:
                self.wallpaper_label.config(image=self.wallpaper_photo)
            else:
                self.wallpaper_label = tk.Label(self, image=self.wallpaper_photo, bd=0)
                self.wallpaper_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.wallpaper_label.lower()
        except Exception as e:
            print(f"Could not load wallpaper from {path}: {e}")
            self.configure(bg="black")
    # maybe we can expand this later to support more formats like gifs and videos
    def animate_wallpaper(self):
        if not self.wallpaper_animating or not self.wallpaper_frames:
            return
        frame = self.wallpaper_frames[self.wallpaper_index]
        self.wallpaper_label.config(image=frame)
        self.wallpaper_index = (self.wallpaper_index + 1) % len(self.wallpaper_frames)
        self.after(100, self.animate_wallpaper)  

    def animate_slideshow(self):
        if not self.wallpaper_frames:
            return
        path = next(self.wallpaper_frames)
        try:
            img = Image.open(path).resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.LANCZOS)
            self.wallpaper_photo = ImageTk.PhotoImage(img)
            if self.wallpaper_label:
                self.wallpaper_label.config(image=self.wallpaper_photo)
            else:
                self.wallpaper_label = tk.Label(self, image=self.wallpaper_photo, bd=0)
                self.wallpaper_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.wallpaper_label.lower()
        except Exception as e:
            print(f"Slideshow error: {e}")
        self.after(8000, self.animate_slideshow)  

    # Ok now UI stuff 
    def setup_ui(self):
        self.icon_container = tk.Frame(self, bg="", bd=0)
        self.icon_container.place(relx=0, rely=0)
        # We still have this because the code breaks when we remove it. It's useless. What the fuck is going on?
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

        # GIF support holy shit
        try:
            gif = Image.open("Assets/screensavers/fractal.gif")
            frames = [ImageTk.PhotoImage(frame.copy().resize(
                (self.winfo_screenwidth(), self.winfo_screenheight()), Image.LANCZOS)) 
                for frame in ImageSequence.Iterator(gif)]
            label = tk.Label(self.screensaver_window, bd=0)
            label.pack(fill="both", expand=True)

            def animate(index=0):
                if not self.screensaver_active: return
                label.config(image=frames[index])
                self.screensaver_window.after(100, animate, (index + 1) % len(frames))

            animate()
        except Exception as e:
            print(f"Screensaver GIF error: {e}")
            tk.Label(self.screensaver_window, text="Franchuk is waiting. Don't leave him alone.", # Is this a threat?
                     fg="white", bg="black", font=("Segoe UI", 48)).pack(expand=True)
            
    # Do not go gentle into that good night,
    # Old age should burn and rave at close of day;
    # Rage, rage against the dying of the light.
    #
    # Though wise men at their end know dark is right,
    # Because their words had forked no lightning they
    # Do not go gentle into that good night.
    #
    # Good men, the last wave by, crying how bright
    # Their frail deeds might have danced in a green bay,
    # Rage, rage against the dying of the light.
    #
    # Wild men who caught and sang the sun in flight,
    # And learn, too late, they grieved it on its way,
    # Do not go gentle into that good night.
    #
    # Grave men, near death, who see with blinding sight
    # Blind eyes could blaze like meteors and be gay,
    # Rage, rage against the dying of the light.
    #
    # And you, my father, there on the sad height,
    # Curse, bless, me now with your fierce tears, I pray.
    # Do not go gentle into that good night.
    # Rage, rage against the dying of the light.

    # Rage against the dying of the light screensaver

    def deactivate_screensaver(self, event=None):
        if self.screensaver_window:
            self.screensaver_window.destroy()
            self.screensaver_window = None
        self.screensaver_active = False
        self.last_activity = time.time()


if __name__ == "__main__":
    desktop = Desktop()
    desktop.mainloop()