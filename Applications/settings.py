# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from Graphics.utils import set_background_color, set_background_image
from config.manager import load_config, save_config
from core.thememanage import apply_theme


OS_VERSION = "32.0"

class SettingsApp:
    def __init__(self):
        self.config = load_config()
        self.root = tk.Toplevel()
        self.root.title("Settings")
        self.root.geometry("700x600")
        self.root.configure(bg="white")
        self.build_ui()
        apply_theme(self.root, self.config.get("theme", "light"))  

    def build_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Appearance Tab
        appearance_frame = ttk.Frame(notebook)
        notebook.add(appearance_frame, text="Appearance")
        self.build_appearance_tab(appearance_frame)

        # Theme Tab
        theme_frame = ttk.Frame(notebook)
        notebook.add(theme_frame, text="Theme")
        self.build_theme_tab(theme_frame)

        # System Tab
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="System Info")
        self.build_system_tab(system_frame)

        # Utilities Tab
        utilities_frame = ttk.Frame(notebook)
        notebook.add(utilities_frame, text="Utilities")
        self.build_utilities_tab(utilities_frame)

        # Network Tab
        network_frame = ttk.Frame(notebook)
        notebook.add(network_frame, text="Network")
        self.build_network_tab(network_frame)

        # Help Tab
        help_frame = ttk.Frame(notebook)
        notebook.add(help_frame, text="Help")
        self.build_help_tab(help_frame)

    def build_appearance_tab(self, parent):
        ttk.Label(parent, text="Wallpaper", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 2), padx=10)
        wall_btns = ttk.Frame(parent)
        wall_btns.pack(anchor="w", padx=10, pady=2)
        ttk.Button(wall_btns, text="Default", command=self.set_default_wallpaper).pack(side="left", padx=2)
        ttk.Button(wall_btns, text="Blue", command=self.set_blue_wallpaper).pack(side="left", padx=2)
        ttk.Button(wall_btns, text="Solid Black", command=lambda: self.set_solid_color("black")).pack(side="left", padx=2)
        ttk.Button(wall_btns, text="Solid Gray", command=lambda: self.set_solid_color("#444")).pack(side="left", padx=2)
        ttk.Button(wall_btns, text="Solid Sky Blue", command=lambda: self.set_solid_color("#87CEEB")).pack(side="left", padx=2)
        ttk.Button(wall_btns, text="Custom Image...", command=self.set_custom_wallpaper).pack(side="left", padx=2)

    def build_theme_tab(self, parent):
        ttk.Label(parent, text="Color Theme", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 2), padx=10)
        self.theme_var = tk.StringVar(value=self.config.get("theme", "light"))
        themes = [
            ("Light", "light"),
            ("Dark", "dark"),
            ("Solarized", "solarized"),
            ("Monokai", "monokai"),
            ("Gruvbox", "gruvbox"),
            ("Dracula", "dracula"),
            ("Nord", "nord"),
            ("High Contrast", "high_contrast"),
        ]
        for label, value in themes:
            ttk.Radiobutton(parent, text=label, variable=self.theme_var, value=value, command=self.set_theme).pack(anchor="w", padx=20, pady=2)

    def build_system_tab(self, parent):
        ttk.Label(parent, text="System Information", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 2), padx=10)
        ttk.Label(parent, text=f"FranchukOS Version: {OS_VERSION}", font=("Segoe UI", 10)).pack(anchor="w", padx=20, pady=5)
        ttk.Label(parent, text="© 2025 FranchukOS Project Authors", font=("Segoe UI", 9)).pack(anchor="w", padx=20, pady=2)
        ttk.Button(parent, text="About", command=self.show_about).pack(anchor="w", padx=20, pady=10)

    def build_utilities_tab(self, parent):
        ttk.Label(parent, text="Utilities", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 2), padx=10)
        ttk.Button(parent, text="Open File Explorer", command=self.open_file_explorer).pack(anchor="w", padx=20, pady=5)
        ttk.Button(parent, text="Launch Terminal", command=self.open_terminal).pack(anchor="w", padx=20, pady=5)
        ttk.Button(parent, text="Take Screenshot", command=self.take_screenshot).pack(anchor="w", padx=20, pady=5)

    def build_network_tab(self, parent):
        ttk.Label(parent, text="Network", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 2), padx=10)
        ttk.Button(parent, text="Show IP Address", command=self.show_ip_address).pack(anchor="w", padx=20, pady=5)
        ttk.Button(parent, text="Test Internet Connection", command=self.test_internet).pack(anchor="w", padx=20, pady=5)

    def build_help_tab(self, parent):
        ttk.Label(parent, text="Help & Support", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(10, 2), padx=10)
        ttk.Button(parent, text="User Guide", command=self.show_user_guide).pack(anchor="w", padx=20, pady=5)
        ttk.Button(parent, text="Contact Support", command=self.contact_support).pack(anchor="w", padx=20, pady=5)
        ttk.Button(parent, text="Check for Updates", command=self.check_updates).pack(anchor="w", padx=20, pady=5)

    def set_default_wallpaper(self):
        set_background_image(self.root, "assets/backgrounds/wallpaper.png")
        self.config["wallpaper"] = "assets/backgrounds/wallpaper.png"
        save_config(self.config)

    def set_blue_wallpaper(self):
        set_background_image(self.root, "assets/backgrounds/blue.png")
        self.config["wallpaper"] = "assets/backgrounds/blue.png"
        save_config(self.config)

    def set_solid_color(self, color):
        set_background_color(self.root, color)
        self.config["wallpaper"] = color
        save_config(self.config)

    def set_custom_wallpaper(self):
        file_path = filedialog.askopenfilename(
            title="Select Wallpaper",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if file_path:
            set_background_image(self.root, file_path)
            self.config["wallpaper"] = file_path
            save_config(self.config)

    def set_theme(self):
        theme = self.theme_var.get()
        self.config["theme"] = theme
        save_config(self.config)
        apply_theme(self.root, theme)

    def show_about(self):
        messagebox.showinfo(
            "About FranchukOS",
            f"FranchukOS Settings\nVersion: {OS_VERSION}\n\nA customizable OS for everyone, especially Mr. Franchuk.\n\n© 2025 FranchukOS Project Authors"
        )

    def open_file_explorer(self):
        import subprocess
        subprocess.Popen('explorer')

    def open_terminal(self):
        import subprocess
        subprocess.Popen('start cmd', shell=True)

    def take_screenshot(self):
        try:
            import pyautogui
            import datetime
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot(filename)
            messagebox.showinfo("Screenshot", f"Screenshot saved as {filename}")
        except ImportError:
            messagebox.showerror("Error", "pyautogui is not installed.")

    def show_ip_address(self):
        import socket
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            messagebox.showinfo("IP Address", f"Hostname: {hostname}\nIP Address: {ip}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not get IP address:\n{e}")

    def test_internet(self):
        import urllib.request
        try:
            urllib.request.urlopen('https://www.google.com', timeout=3)
            messagebox.showinfo("Internet Test", "Internet connection is working.")
        except Exception:
            messagebox.showwarning("Internet Test", "No internet connection detected.")

    def show_user_guide(self):
        messagebox.showinfo("User Guide", "Visit the Discord server here for documentation: https://discord.gg/BcFuwEkNHH")

    def contact_support(self):
        messagebox.showinfo("Contact Support", "Email:")

    def check_updates(self):
        messagebox.showinfo("Updates", "You are running the latest version of FranchukOS.")

    def run():
        SettingsApp()
