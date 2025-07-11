# Copyright 2025 the Franchuk project authors.

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
from config.manager import load_profiles, save_profiles
from PIL import Image, ImageTk, ImageFilter
import os
import pygame

class LoginApp:
    def __init__(self):
        self.profiles = load_profiles()
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.wallpaper_path = "assets/backgrounds/login.png"
        self.background_label = None
        self.wallpaper_image = None

        self.set_login_wallpaper(self.wallpaper_path)
        self.root.bind("<Configure>", self.on_resize)

        self.build_ui()

    def set_login_wallpaper(self, wallpaper_path):
        width = self.root.winfo_width() or 800
        height = self.root.winfo_height() or 600
        wallpaper = Image.open(wallpaper_path).resize((width, height), Image.LANCZOS)

        # Blur background
        wallpaper = wallpaper.filter(ImageFilter.GaussianBlur(3))

        self.wallpaper_image = ImageTk.PhotoImage(wallpaper)

        if self.background_label is None:
            self.background_label = tk.Label(self.root, image=self.wallpaper_image)
            self.background_label.place(relwidth=1, relheight=1)
        else:
            self.background_label.configure(image=self.wallpaper_image)
        self.background_label.image = self.wallpaper_image

    def on_resize(self, event):
        if event.widget == self.root:
            self.set_login_wallpaper(self.wallpaper_path)

    def build_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Glass.TFrame", background="#1c1c1c", relief="flat")
        style.configure("TLabel", background="#1c1c1c", foreground="white", font=("Segoe UI", 13))
        style.configure("TButton", background="#3b3b3b", foreground="white", relief="flat", font=("Segoe UI", 12))
        style.map("TButton", background=[("active", "#505050")])
        style.configure("TEntry", font=("Segoe UI", 12))

        container = ttk.Frame(self.root, padding=30, style="Glass.TFrame")
        container.place(relx=0.5, rely=0.5, anchor="center")

        title = ttk.Label(container, text="Welcome to FranchukOS", font=("Segoe UI", 22, "bold"))
        title.pack(pady=(10, 20))

        try:
            self.user_icon = ImageTk.PhotoImage(Image.open("assets/icons/user.png").resize((20, 20)))
            self.lock_icon = ImageTk.PhotoImage(Image.open("assets/icons/lock.png").resize((20, 20)))
        except:
            self.user_icon = self.lock_icon = None

        if self.user_icon:
            tk.Label(container, image=self.user_icon, background="#1c1c1c").pack()
        self.username_label = ttk.Label(container, text="Username:")
        self.username_label.pack(pady=2)
        self.username_entry = ttk.Entry(container, width=30)
        self.username_entry.pack(pady=5)

        if self.lock_icon:
            tk.Label(container, image=self.lock_icon, background="#1c1c1c").pack()
        self.password_label = ttk.Label(container, text="Password:")
        self.password_label.pack(pady=2)
        self.password_entry = ttk.Entry(container, show="*", width=30)
        self.password_entry.pack(pady=5)

        self.login_button = ttk.Button(container, text="Login", command=self.login)
        self.login_button.pack(pady=(15, 6), fill="x")

        self.new_user_button = ttk.Button(container, text="New User", command=self.new_user)
        self.new_user_button.pack(pady=5, fill="x")

        self.root.bind("<Return>", lambda event: self.login())
        self.root.bind("<Escape>", lambda event: self.root.destroy())

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        for user in self.profiles:
            if isinstance(user, dict) and user.get("username") == username and user.get("password") == password:
                pygame.mixer.init()
                pygame.mixer.music.load("assets/sounds/login.wav")
                pygame.mixer.music.play()
                messagebox.showinfo("Login Successful", f"Welcome, {username}!")
                self.root.destroy()
                return

        messagebox.showerror("Login Failed", "Invalid username or password.")

    def new_user(self):
        username = simpledialog.askstring("New User", "Enter new username:", parent=self.root)
        if not username or not username.strip():
            return

        for user in self.profiles:
            if user.get("username") == username:
                messagebox.showerror("Error", "Username already exists!")
                return

        password = simpledialog.askstring("New User", "Enter new password:", show="*", parent=self.root)
        if not password or not password.strip():
            return

        avatar_path = filedialog.askopenfilename(
            title="Select Avatar Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )

        if avatar_path:
            avatar_img = Image.open(avatar_path)
            avatar_img.thumbnail((64, 64))
            avatar_preview = ImageTk.PhotoImage(avatar_img)
            preview_window = tk.Toplevel(self.root)
            tk.Label(preview_window, image=avatar_preview).pack()
            tk.Label(preview_window, text="Avatar Preview").pack()
            preview_window.after(1500, preview_window.destroy)

        new_user = {
            "username": username.strip(),
            "password": password.strip(),
            "avatar_path": avatar_path
        }

        self.profiles.append(new_user)
        save_profiles(self.profiles)

        messagebox.showinfo("Success", "New user created successfully!")
        pygame.mixer.init()
        pygame.mixer.music.load("assets/sounds/success.wav")
        pygame.mixer.music.play()

    def run(self):
        self.root.mainloop()

