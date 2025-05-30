# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import ttk
from Graphics.utils import set_background_color, set_background_image
from Config.manager import load_config, save_config
from Core.thememanage import apply_theme


OS_VERSION = "FranchukOS Rainier, v31.1.1.6379.132 (x64) 2025-05-25"

class SettingsApp:
    def __init__(self):
        self.config = load_config()
        self.root = tk.Toplevel()
        self.root.title("Settings")
        self.root.geometry("500x500")
        self.root.configure(bg="white")
        self.build_ui()
        apply_theme(self.root, self.config["theme"])  

    def build_ui(self):
        title = ttk.Label(self.root, text="Settings", font=("Segoe UI", 16))
        title.pack(pady=10)

        # Wallpaper selector
        wallpaper_frame = ttk.LabelFrame(self.root, text="Wallpaper")
        wallpaper_frame.pack(padx=20, pady=10, fill="x")

        ttk.Button(wallpaper_frame, text="Set Default Wallpaper", command=self.set_default_wallpaper).pack(padx=10, pady=5)
        ttk.Button(wallpaper_frame, text="Set Blue Wallpaper", command=self.set_blue_wallpaper).pack(padx=10, pady=5)
        ttk.Button(wallpaper_frame, text="Solid Black", command=lambda: set_background_color(self.root, "black")).pack(padx=10, pady=5)
        ttk.Button(wallpaper_frame, text="Solid Gray", command=lambda: set_background_color(self.root, "#444")).pack(padx=10, pady=5)
        ttk.Button(wallpaper_frame, text="Solid Sky Blue", command=lambda: set_background_color(self.root, "#87CEEB")).pack(padx=10, pady=5)

        # Theme toggle
        theme_frame = ttk.LabelFrame(self.root, text="Theme")
        theme_frame.pack(padx=20, pady=10, fill="x")

        self.theme_var = tk.StringVar(value=self.config["theme"])
        ttk.Radiobutton(theme_frame, text="Light Mode", variable=self.theme_var, value="light", command=self.set_theme).pack(anchor="w", padx=10)
        ttk.Radiobutton(theme_frame, text="Dark Mode", variable=self.theme_var, value="dark", command=self.set_theme).pack(anchor="w", padx=10)

        # System Info
        info_frame = ttk.LabelFrame(self.root, text="System Info")
        info_frame.pack(padx=20, pady=10, fill="x")

        ttk.Label(info_frame, text=f"Version: {OS_VERSION}", font=("Segoe UI", 10)).pack(padx=10, pady=5)
        ttk.Label(info_frame, text="© 2025 FranchukOS Project Authors", font=("Segoe UI", 9)).pack(padx=10, pady=2)

    def set_default_wallpaper(self):
        set_background_image(self.root, "assets/backgrounds/wallpaper.png")
        self.config["wallpaper"] = "assets/backgrounds/wallpaper.png"
        save_config(self.config)

    def set_blue_wallpaper(self):
        set_background_image(self.root, "assets/backgrounds/blue.png")
        self.config["wallpaper"] = "assets/backgrounds/blue.png"
        save_config(self.config)

    def set_theme(self):
        theme = self.theme_var.get()
        self.config["theme"] = theme
        save_config(self.config)
        apply_theme(self.root, theme)  

def run():
    SettingsApp()
