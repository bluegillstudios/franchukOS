import tkinter as tk
from tkinter import messagebox, simpledialog
from config.manager import load_profiles, save_profiles
from PIL import Image, ImageTk 
from playsound import playsound
import os

class LoginApp:
    def __init__(self):
        self.profiles = load_profiles()  # Load profiles from the config file
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("500x300")
        self.root.configure(bg="black")
        
        # Set login wallpaper
        self.set_login_wallpaper("assets/backgrounds/login.png")

        self.build_ui()

    def set_login_wallpaper(self, wallpaper_path):
        """Set a background wallpaper for the login screen."""
        wallpaper = Image.open(wallpaper_path)
        wallpaper = wallpaper.resize((500, 300), Image.ANTIALIAS)
        wallpaper = ImageTk.PhotoImage(wallpaper)
        
        background_label = tk.Label(self.root, image=wallpaper)
        background_label.place(relwidth=1, relheight=1)
        background_label.image = wallpaper  # Keep a reference to the image

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
        for user in self.profiles["users"]:
            if user["username"] == username and user["password"] == password:
                playsound("assets/sounds/login.wav") 
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

        # Check if the username already exists
        for user in self.profiles["users"]:
            if user["username"] == username:
                messagebox.showerror("Error", "Username already exists!")
                playsound("assets/sounds/error.wav")
                return
        
        password = simpledialog.askstring("New User", "Enter new password:", show="*", parent=self.root)
        if password is None:
            return  

        # Add the new user to profiles.json
        new_user = {"username": username, "password": password}
        self.profiles["users"].append(new_user)
        save_profiles(self.profiles)
        messagebox.showinfo("Success", "New user created successfully!")
        playsound("assets/sounds/success.wav")

    def run(self):
        """Run the Tkinter main loop."""
        self.root.mainloop()
