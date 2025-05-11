# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import messagebox
from playsound import playsound
from desktop import Desktop
from gui.taskbar import Taskbar
from gui.login import LoginApp

def start_startup_sound():
    """Play the startup sound when the OS starts up."""
    playsound("assets/sounds/startup.wav")  

def launch_desktop():
    """Launch the desktop and taskbar after login."""
    desktop = Desktop()  # Create the desktop app instance
    taskbar = Taskbar(desktop.root)  # Create taskbar for the desktop
    taskbar.start()  # Start the taskbar
    desktop.run()  # Run the desktop GUI loop

def launch_login():
    """Launch the login screen and handle successful login."""
    login_app = LoginApp()

    # Check login result
    login_app.run()  # Wait for the login screen to run and get user login

    # If login is successful, launch the desktop
    launch_desktop()

def main():
    """Main entry point for FranchukOS."""
    start_startup_sound()  # Play the startup sound when booted
    launch_login()  # Proceed to the login screen

if __name__ == "__main__":
    main()
