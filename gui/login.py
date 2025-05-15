import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from config.manager import load_profiles, save_profiles
from PIL import Image, ImageTk 
from playsound import playsound
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
        width = self.root.winfo_width() or 500
        height = self.root.winfo_height() or 300
        wallpaper = Image.open(wallpaper_path)
        wallpaper = wallpaper.resize((width, height), Image.LANCZOS)
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
        style.configure("TFrame", background="#000000", relief="flat")
        style.configure("TLabel", background="#000000", foreground="white", font=("Segoe UI", 14))
        style.configure("TButton", font=("Segoe UI", 12), padding=6)
        style.configure("TEntry", font=("Segoe UI", 12))

        container = ttk.Frame(self.root, padding=20)
        container.place(relx=0.5, rely=0.5, anchor="center")

        title = ttk.Label(container, text="Welcome to FranchukOS", font=("Segoe UI", 24, "bold"))
        title.pack(pady=20)

        self.username_label = ttk.Label(container, text="Username:")
        self.username_label.pack(pady=5)

        self.username_entry = ttk.Entry(container, width=30)
        self.username_entry.pack(pady=5)

        self.password_label = ttk.Label(container, text="Password:")
        self.password_label.pack(pady=5)

        self.password_entry = ttk.Entry(container, show="*", width=30)
        self.password_entry.pack(pady=5)

        self.login_button = ttk.Button(container, text="Login", command=self.login)
        self.login_button.pack(pady=10)

        self.new_user_button = ttk.Button(container, text="New User", command=self.new_user)
        self.new_user_button.pack(pady=5)

        self.root.bind("<Return>", lambda event: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        users = self.profiles.values() if isinstance(self.profiles, dict) else self.profiles
        for user in users:
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
        if username is None:
            return

        users = self.profiles.values() if isinstance(self.profiles, dict) else self.profiles
        for user in users:
            if isinstance(user, dict) and user.get("username") == username:
                messagebox.showerror("Error", "Username already exists!")
                pygame.mixer.init()
                pygame.mixer.music.load("assets/sounds/error.wav")
                pygame.mixer.music.play()
                return

        password = simpledialog.askstring("New User", "Enter new password:", show="*", parent=self.root)
        if password is None:
            return

        new_user = {"username": username, "password": password}
        self.profiles.append(new_user)
        save_profiles(self.profiles)
        messagebox.showinfo("Success", "New user created successfully!")
        pygame.mixer.init()
        pygame.mixer.music.load("assets/sounds/success.wav")
        pygame.mixer.music.play()

    def run(self):
        self.root.mainloop()
        pygame.mixer.quit()