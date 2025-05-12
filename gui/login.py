import tkinter as tk
from tkinter import messagebox, simpledialog
from config.manager import load_profiles, save_profiles
from PIL import Image, ImageTk 
from playsound import playsound
import os
import pygame

class LoginApp:
    def __init__(self):
        self.profiles = load_profiles()  # Load profiles from the config file
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        self.wallpaper_path = "assets/backgrounds/login.png"
        self.background_label = None
        self.wallpaper_image = None  # Keep a reference to avoid garbage collection

        self.set_login_wallpaper(self.wallpaper_path)
        self.root.bind("<Configure>", self.on_resize)

        self.build_ui()

    def set_login_wallpaper(self, wallpaper_path):
        """Set a background wallpaper for the login screen."""
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
        self.background_label.image = self.wallpaper_image  # Keep a reference

    def on_resize(self, event):
        # Only resize if the window size actually changed
        if event.widget == self.root:
            self.set_login_wallpaper(self.wallpaper_path)

    def build_ui(self):
        """Build the login UI components."""
        title = tk.Label(self.root, text="Login", font=("Segoe UI", 20), bg="black", fg="white")
        title.pack(pady=10)

        # Username input
        self.username_label = tk.Label(self.root, text="Username:", bg="black", fg="white")
        self.username_label.pack(pady=5)

        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)

        # Password input
        self.password_label = tk.Label(self.root, text="Password:", bg="black", fg="white")
        self.password_label.pack(pady=5)

        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        # Login button
        self.login_button = tk.Button(self.root, text="Login", command=self.login, width=20)
        self.login_button.pack(pady=10)

        # New User button
        self.new_user_button = tk.Button(self.root, text="New User", command=self.new_user, width=20)
        self.new_user_button.pack(pady=10)

    def login(self):
        """Handle the login process."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check credentials
        users = self.profiles.values() if isinstance(self.profiles, dict) else self.profiles
        for user in users:
            if isinstance(user, dict) and user.get("username") == username and user.get("password") == password:
                pygame.mixer.init()
                pygame.mixer.music.load("assets/sounds/login.wav")
                pygame.mixer.music.play()
                messagebox.showinfo("Login Successful", f"Welcome, {username}!")
                self.root.destroy()  # Close login window
                return

        # If credentials are incorrect
        messagebox.showerror("Login Failed", "Invalid username or password.")

    def new_user(self):
        """Allow new user registration."""
        username = simpledialog.askstring("New User", "Enter new username:", parent=self.root)
        if username is None:
            return  # If the user cancels, do nothing

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

        # Add the new user to profiles.json
        new_user = {"username": username, "password": password}
        self.profiles.append(new_user)
        save_profiles(self.profiles)
        messagebox.showinfo("Success", "New user created successfully!")
        pygame.mixer.init()
        pygame.mixer.music.load("assets/sounds/success.wav")
        pygame.mixer.music.play()

    def run(self):
        """Run the Tkinter main loop."""
        self.root.mainloop()
