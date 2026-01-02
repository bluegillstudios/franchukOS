# Copyright 2025 the Franchuk project authors.

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
from config.manager import load_profiles, save_profiles
from PIL import Image, ImageTk, ImageFilter
import os
import pygame



# ---- TRANSLATION DICTIONARY ----
TRANSLATIONS = {
    "en": {
        "title": "Login",
        "welcome": "Welcome to FranchukOS",
        "username": "Username:",
        "password": "Password:",
        "login": "Login",
        "new_user": "New User",
        "login_successful": "Login Successful",
        "login_successful_msg": "Welcome, {username}!",
        "login_failed": "Login Failed",
        "login_failed_msg": "Invalid username or password.",
        "error": "Error",
        "username_exists": "Username already exists!",
        "success": "Success",
        "new_user_created": "New user created successfully!",
        "new_user_prompt": "Enter new username:",
        "new_password_prompt": "Enter new password:",
        "select_avatar": "Select Avatar Image",
        "avatar_preview": "Avatar Preview",
        "language": "Language",
    },
    "fr": {
        "title": "Connexion",
        "welcome": "Bienvenue sur FranchukOS",
        "username": "Nom d'utilisateur :",
        "password": "Mot de passe :",
        "login": "Se connecter",
        "new_user": "Nouvel utilisateur",
        "login_successful": "Connexion réussie",
        "login_successful_msg": "Bienvenue, {username} !",
        "login_failed": "Échec de la connexion",
        "login_failed_msg": "Nom d'utilisateur ou mot de passe invalide.",
        "error": "Erreur",
        "username_exists": "Le nom d'utilisateur existe déjà !",
        "success": "Succès",
        "new_user_created": "Nouvel utilisateur créé avec succès !",
        "new_user_prompt": "Entrez un nouveau nom d'utilisateur :",
        "new_password_prompt": "Entrez un nouveau mot de passe :",
        "select_avatar": "Sélectionnez une image d'avatar",
        "avatar_preview": "Aperçu de l'avatar",
        "language": "Langue",
    },
    "es": {
        "title": "Iniciar sesión",
        "welcome": "Bienvenido a FranchukOS",
        "username": "Nombre de usuario:",
        "password": "Contraseña:",
        "login": "Iniciar sesión",
        "new_user": "Nuevo usuario",
        "login_successful": "Inicio de sesión exitoso",
        "login_successful_msg": "¡Bienvenido, {username}!",
        "login_failed": "Inicio fallido",
        "login_failed_msg": "Nombre de usuario o contraseña inválido.",
        "error": "Error",
        "username_exists": "¡El nombre de usuario ya existe!",
        "success": "Éxito",
        "new_user_created": "¡Nuevo usuario creado exitosamente!",
        "new_user_prompt": "Ingrese un nuevo nombre de usuario:",
        "new_password_prompt": "Ingrese una nueva contraseña:",
        "select_avatar": "Seleccionar imagen de avatar",
        "avatar_preview": "Vista previa del avatar",
        "language": "Idioma",
    }
}

LANGUAGES = [("English", "en"), ("Français", "fr"), ("Español", "es")]

class LoginApp:
    def __init__(self):
        self.profiles = load_profiles()
        self.language = "en"
        self.trans = TRANSLATIONS[self.language]
        self.root = tk.Tk()
        self.root.title(self.trans["title"])
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
        # Remove prior widgets if re-building for language change
        for widget in self.root.winfo_children():
            if widget != self.background_label:
                widget.destroy()

        self.trans = TRANSLATIONS[self.language]
        self.root.title(self.trans["title"])

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Glass.TFrame", background="#1c1c1c", relief="flat")
        style.configure("TLabel", background="#1c1c1c", foreground="white", font=("Segoe UI", 13))
        style.configure("TButton", background="#3b3b3b", foreground="white", relief="flat", font=("Segoe UI", 12))
        style.map("TButton", background=[("active", "#505050")])
        style.configure("TEntry", font=("Segoe UI", 12))

        # Language selector
        lang_frame = ttk.Frame(self.root, style="Glass.TFrame")
        lang_frame.place(relx=0.01, rely=0.01, anchor='nw')
        ttk.Label(lang_frame, text=self.trans["language"]).pack(side="left", padx=2)
        self.lang_var = tk.StringVar(value=self.language)
        lang_menu = ttk.OptionMenu(
            lang_frame, self.lang_var, self.language,
            *[code for (_, code) in LANGUAGES],
            command=self.on_language_change
        )
        lang_menu.pack(side="left")

        container = ttk.Frame(self.root, padding=30, style="Glass.TFrame")
        container.place(relx=0.5, rely=0.5, anchor="center")

        title = ttk.Label(container, text=self.trans["welcome"], font=("Segoe UI", 22, "bold"))
        title.pack(pady=(10, 20))

        try:
            self.user_icon = ImageTk.PhotoImage(Image.open("assets/icons/user.png").resize((20, 20)))
            self.lock_icon = ImageTk.PhotoImage(Image.open("assets/icons/lock.png").resize((20, 20)))
        except:
            self.user_icon = self.lock_icon = None

        if self.user_icon:
            tk.Label(container, image=self.user_icon, background="#1c1c1c").pack()
        self.username_label = ttk.Label(container, text=self.trans["username"])
        self.username_label.pack(pady=2)
        self.username_entry = ttk.Entry(container, width=30)
        self.username_entry.pack(pady=5)

        if self.lock_icon:
            tk.Label(container, image=self.lock_icon, background="#1c1c1c").pack()
        self.password_label = ttk.Label(container, text=self.trans["password"])
        self.password_label.pack(pady=2)
        self.password_entry = ttk.Entry(container, show="*", width=30)
        self.password_entry.pack(pady=5)

        self.login_button = ttk.Button(container, text=self.trans["login"], command=self.login)
        self.login_button.pack(pady=(15, 6), fill="x")

        self.new_user_button = ttk.Button(container, text=self.trans["new_user"], command=self.new_user)
        self.new_user_button.pack(pady=5, fill="x")

        self.root.bind("<Return>", lambda event: self.login())
        self.root.bind("<Escape>", lambda event: self.root.destroy())

    def on_language_change(self, code):
        self.language = code
        self.trans = TRANSLATIONS[self.language]
        self.build_ui()

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        for user in self.profiles:
            if isinstance(user, dict) and user.get("username") == username and user.get("password") == password:
                pygame.mixer.init()
                pygame.mixer.music.load("assets/sounds/login.wav")
                pygame.mixer.music.play()
                messagebox.showinfo(self.trans["login_successful"], self.trans["login_successful_msg"].format(username=username))
                self.root.destroy()
                return

        messagebox.showerror(self.trans["login_failed"], self.trans["login_failed_msg"])

    def new_user(self):
        username = simpledialog.askstring(self.trans["new_user"], self.trans["new_user_prompt"], parent=self.root)
        if not username or not username.strip():
            return

        for user in self.profiles:
            if user.get("username") == username:
                messagebox.showerror(self.trans["error"], self.trans["username_exists"])
                return

        password = simpledialog.askstring(self.trans["new_user"], self.trans["new_password_prompt"], show="*", parent=self.root)
        if not password or not password.strip():
            return

        avatar_path = filedialog.askopenfilename(
            title=self.trans["select_avatar"],
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")]
        )

        if avatar_path:
            avatar_img = Image.open(avatar_path)
            avatar_img.thumbnail((64, 64))
            avatar_preview = ImageTk.PhotoImage(avatar_img)
            preview_window = tk.Toplevel(self.root)
            tk.Label(preview_window, image=avatar_preview).pack()
            tk.Label(preview_window, text=self.trans["avatar_preview"]).pack()
            preview_window.after(1500, preview_window.destroy)
            # Prevent garbage collection of avatar_preview
            preview_window.avatar_preview = avatar_preview

        new_user = {
            "username": username.strip(),
            "password": password.strip(),
            "avatar_path": avatar_path
        }

        self.profiles.append(new_user)
        save_profiles(self.profiles)

        messagebox.showinfo(self.trans["success"], self.trans["new_user_created"])
        pygame.mixer.init()
        pygame.mixer.music.load("assets/sounds/success.wav")
        pygame.mixer.music.play()

    def run(self):
        self.root.mainloop()
        pygame.mixer.music.play()
