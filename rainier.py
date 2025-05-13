# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
import threading
from gui.login import LoginApp  
from desktop import Desktop
from gui.taskbar import Taskbar
import pygame

SPLASH_DURATION = 3  # seconds

def show_splash(next_step_callback):
    splash = tk.Tk()
    splash.overrideredirect(False)
    splash.attributes('-fullscreen', True)
    splash.configure(bg="black")

    label = tk.Label(
        splash,
        text="FranchukOS",
        font=("Helvetica", 32, "bold"),
        bg="black",
        fg="skyblue"
    )
    label.pack(expand=True)

    # Play startup sound in a thread
    def play_startup_sound():
        pygame.mixer.init()
        pygame.mixer.music.load("assets/sounds/startup.wav")
        pygame.mixer.music.play()
    threading.Thread(
        target=play_startup_sound,
        daemon=True
    ).start()

    def close_splash():
        splash.destroy()
        next_step_callback()

    splash.after(SPLASH_DURATION * 1000, close_splash)
    splash.mainloop()

def start_login():
    login = LoginApp()
    login.run()  # Wait for login to complete

    # Logged in, proceed to desktop
    # Initialize the desktop and taskbar
    desktop = Desktop()
    taskbar = Taskbar()
    desktop.run()
    taskbar.run()

def main():
    show_splash(start_login)

if __name__ == "__main__":
    main()
