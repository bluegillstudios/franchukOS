# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import messagebox
import time
from threading import Thread
from datetime import datetime
from Applications.file_explorer import FileExplorer
from Applications.terminal import Terminal
from Applications.settings import SettingsApp
from Applications.clock import ClockApp
from Applications.insider import Insider
from Applications.outsider import Outsider
from Applications.games.snake import snake_game as SnakeGame
from Applications.games.spi import SpaceInvaders
from Applications.games.aloha import AlohaGameGUI as Aloha
from Applications.franpaint import Franpaint
from Applications.taskmgr import TaskManager
from Applications.franny import FrannyBrowser
from Applications.birdseye import Birdseye
import playsound
import subprocess
import sys

class WindowManager:
    def __init__(self, taskbar):
        self.taskbar = taskbar
        self.open_windows = {}
        self.active_window = None

    def open_window(self, window_name, window_class):
        if window_name not in self.open_windows:
            # Some apps require a parent, others do not
            try:
                window = window_class(self.taskbar)
            except TypeError:
                window = window_class()
            window.grab_set()  # Block interactions with other windows until this one is closed.
            self.open_windows[window_name] = window
            self.taskbar.add_taskbar_button(window_name)
            self.switch_to_window(window_name)  # Switch to the new window.
            return window
        else:
            # Bring the window to front if it is already open
            self.switch_to_window(window_name)
            return self.open_windows[window_name]

    def close_window(self, window_name):
        if window_name in self.open_windows:
            self.open_windows[window_name].destroy()
            del self.open_windows[window_name]
            self.taskbar.remove_taskbar_button(window_name)

    def switch_to_window(self, window_name):
        # Hide the currently active window if any
        if self.active_window and self.active_window.winfo_exists():
            self.active_window.withdraw()
        # Show the new window and make it active
        self.active_window = self.open_windows[window_name]
        self.active_window.deiconify()
        self.taskbar.update_taskbar_button(window_name)

class AppWindow(tk.Toplevel):
    def __init__(self, parent, window_name, window_manager):
        super().__init__(parent)
        self.title(window_name)
        self.geometry("400x300")
        self.configure(bg="white")
        self.window_manager = window_manager

        # Add window buttons: Minimize, Maximize, Close
        self.title_bar = tk.Frame(self, bg="gray", height=30)
        self.title_bar.pack(fill="x", side="top")

        self.min_button = tk.Button(self.title_bar, text="Min", command=self.minimize, width=4)
        self.min_button.pack(side="left")

        self.max_button = tk.Button(self.title_bar, text="Max", command=self.maximize, width=4)
        self.max_button.pack(side="left")

        self.close_button = tk.Button(self.title_bar, text="X", command=self.close, width=4)
        self.close_button.pack(side="left")

        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_move)

        self.drag_start_x = 0
        self.drag_start_y = 0

    def start_move(self, event):
        # Record the starting point for dragging
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_move(self, event):
        # Move the window by calculating the difference
        deltax = event.x - self.drag_start_x
        deltay = event.y - self.drag_start_y
        self.geometry(f"+{self.winfo_x() + deltax}+{self.winfo_y() + deltay}")

    def minimize(self):
        self.withdraw()  # Hide the window, acting like minimize

    def maximize(self):
        # Toggle between normal size and maximized size
        if self.winfo_width() == self.winfo_screenwidth() and self.winfo_height() == self.winfo_screenheight():
            self.geometry("400x300")  # Restore to normal size
        else:
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")  # Maximize the window

    def close(self):
        self.window_manager.close_window(self.title())  # Close the window and remove it from the window manager

class Taskbar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(bg="#1e1e1e")  # Dark theme background

        self.window_manager = WindowManager(self)

        # Bottom bar
        self.taskbar_frame = tk.Frame(self, bg="#1e1e1e", height=50)
        self.taskbar_frame.pack(fill="x", side="bottom")

        # Start Button
        self.start_button = tk.Button(
            self.taskbar_frame, text="🟢 Start",
            command=self.show_start_menu,
            bg="#333333", fg="white",
            font=("Segoe UI", 11, "bold"),
            activebackground="#444444",
            relief="flat", bd=0,
            padx=10, pady=5
        )
        self.start_button.pack(side="left", padx=8, pady=5)

        # Clock
        self.clock_label = tk.Label(
            self.taskbar_frame,
            text=self.get_time(),
            bg="#1e1e1e", fg="white",
            font=("Segoe UI", 11)
        )
        self.clock_label.pack(side="right", padx=12)

        # System tray placeholder
        self.system_tray = tk.Frame(self.taskbar_frame, bg="#1e1e1e")
        self.system_tray.pack(side="right", padx=8)

        # Open window buttons
        self.taskbar_buttons_frame = tk.Frame(self, bg="#1e1e1e")
        self.taskbar_buttons_frame.pack(side="bottom", fill="x")

        # Start updating time
        self.update_time_thread = Thread(target=self.update_time, daemon=True)
        self.update_time_thread.start()

    def add_taskbar_button(self, window_name):
        button = tk.Button(
            self.taskbar_buttons_frame, text=window_name,
            command=lambda: self.window_manager.switch_to_window(window_name),
            bg="#2d2d2d", fg="white",
            activebackground="#444444",
            font=("Segoe UI", 10),
            relief="flat", bd=0,
            padx=8, pady=4
        )
        button.bind("<Enter>", lambda e: button.config(bg="#3a3a3a"))
        button.bind("<Leave>", lambda e: button.config(bg="#2d2d2d"))
        button.bind("<Button-3>", lambda event, name=window_name: self.show_taskbar_context_menu(event, name))
        button.pack(side="left", padx=5, pady=5)

    def update_taskbar_button(self, window_name):
        for button in self.taskbar_buttons_frame.winfo_children():
            if button['text'] == window_name:
                button.configure(bg="#555555")
            else:
                button.configure(bg="#2d2d2d")

    def get_time(self):
        return datetime.now().strftime("%H:%M:%S")
    
    def update_time(self):
        self.clock_label.configure(text=self.get_time())
        self.after(1000, self.update_time)  
    def show_start_menu(self):
        menu = tk.Menu(self, tearoff=0, bg="#1e1e1e", fg="white", activebackground="#444444", font=("Segoe UI", 10))

        # Productivity submenu
        productivity_menu = tk.Menu(menu, tearoff=0, bg="#1e1e1e", fg="white", activebackground="#444444")
        productivity_menu.add_command(label="Franny", command=self.launch_franny)
        productivity_menu.add_command(label="Franny's Pop Shop", command=self.launch_shop)
        productivity_menu.add_command(label="Birdseye", command=self.launch_birdseye)
        productivity_menu.add_command(label="Sheets", command=self.launch_sheets)
        productivity_menu.add_command(label="Calculator", command=self.launch_calc)
        productivity_menu.add_command(label="Notetaking", command=self.launch_note)
        productivity_menu.add_command(label="Franmail", command=self.launch_email)
        menu.add_cascade(label="Productivity", menu=productivity_menu)

        # System submenu
        system_menu = tk.Menu(menu, tearoff=0, bg="#1e1e1e", fg="white", activebackground="#444444")
        system_menu.add_command(label="Task Manager", command=self.launch_taskmgr)
        system_menu.add_command(label="File Explorer", command=self.launch_file_explorer)  
        system_menu.add_command(label="Terminal", command=self.launch_terminal)
        system_menu.add_command(label="Settings", command=self.launch_settings)
        system_menu.add_command(label="Clock", command=self.launch_clock)
        menu.add_cascade(label="System", menu=system_menu)

        # Creative submenu
        creative_menu = tk.Menu(menu, tearoff=0, bg="#1e1e1e", fg="white", activebackground="#444444")
        creative_menu.add_command(label="Franpaint", command=self.launch_franpaint)
        creative_menu.add_command(label="Insider", command=self.launch_insider)
        creative_menu.add_command(label="Outsider", command=self.launch_outsider)
        creative_menu.add_command(label="Tempo", command=self.launch_tempo)
        menu.add_cascade(label="Creative", menu=creative_menu)

        # Games submenu
        games_menu = tk.Menu(menu, tearoff=0, bg="#1e1e1e", fg="white", activebackground="#444444")
        games_menu.add_command(label="Snake", command=self.launch_snake)
        games_menu.add_command(label="Space Invaders", command=self.launch_space_invaders)
        games_menu.add_command(label="Aloha", command=self.launch_aloha)
        games_menu.add_command(label="Minesweeper", command=self.launch_mines)
        games_menu.add_command(label="Tetris", command=self.launch_tetris)
        games_meniu.add_command(label="Runner", command=self.launch_runner)
        menu.add_cascade(label="Games", menu=games_menu)

        menu.add_separator()
        menu.add_command(label="Exit", command=self.exit_os)

        menu.post(
            self.winfo_rootx() + self.start_button.winfo_x(),
            self.winfo_rooty() + self.start_button.winfo_y() + 50
        )

    def exit_os(self):
        confirm = messagebox.askyesno("Exit", "Are you sure you want to exit FranchukOS?")
        if confirm:
            self.quit()
            playsound.playsound("assets/sounds/shutdown.wav")  

    def add_taskbar_button(self, window_name):
        button = tk.Button(self.taskbar_buttons_frame, text=window_name, command=lambda: self.window_manager.switch_to_window(window_name))
        button.bind("<Button-3>", lambda event, name=window_name: self.show_taskbar_context_menu(event, name))
        button.pack(side="left", padx=5)

    def remove_taskbar_button(self, window_name):
        # Find and remove button from taskbar
        for button in self.taskbar_buttons_frame.winfo_children():
            if button['text'] == window_name:
                button.destroy()

    def update_taskbar_button(self, window_name):
        # Update the taskbar button to indicate the active window
        for button in self.taskbar_buttons_frame.winfo_children():
            if button['text'] == window_name:
                button.configure(bg="lightgray")
            else:
                button.configure(bg="black")

    def show_taskbar_context_menu(self, event, window_name):
        menu = tk.Menu(self, tearoff=0, bg="black", fg="lime")
        menu.add_command(label="Minimize", command=lambda: self.window_manager.open_window(window_name, None).minimize())
        menu.add_command(label="Close", command=lambda: self.window_manager.close_window(window_name))
        menu.add_separator()
        menu.add_command(label="Switch to", command=lambda: self.window_manager.switch_to_window(window_name))

        menu.post(event.x_root, event.y_root)

    # This shit has got so fucked. 
    # Maybe we can do something about this when v40 rolls around. 
    def launch_file_explorer(self):
        self.window_manager.open_window("File Explorer", FileExplorer)
    def launch_terminal(self):
        self.window_manager.open_window("Terminal", Terminal)
    def launch_settings(self):
        self.window_manager.open_window("Settings", SettingsApp)
    def launch_clock(self):
        self.window_manager.open_window("Clock", ClockApp)
    def launch_insider(self):
        self.window_manager.open_window("Insider", Insider)
    def launch_outsider(self):
        self.window_manager.open_window("Outsider", Outsider)
    def launch_franny(self):
        try:
            subprocess.Popen([sys.executable, "Applications/franny.py"])
        except Exception as e:
            print(f"Failed to launch Franny: {e}")
    def launch_snake(self):
        self.window_manager.open_window("Snake", SnakeGame)
    def launch_space_invaders(self):
        self.window_manager.open_window("Space Invaders", SpaceInvaders)
    def launch_aloha(self):
        self.window_manager.open_window("Aloha", Aloha)
    def launch_franpaint(self):
        try:
            subprocess.Popen([sys.executable, "Applications/franpaint.py"])
        except Exception as e:
            print(f"Failed to launch Franpaint: {e}")
    def launch_taskmgr(self):
        self.window_manager.open_window("Task Manager", TaskManager)
    def launch_birdseye(self):
        try:
            subprocess.Popen([sys.executable, "Applications/birdseye.py"])
        except Exception as e:
            print(f"Failed to launch Birdseye: {e}")
    def launch_sheets(self):
        try:
            subprocess.Popen([sys.executable, "Applications/sheets.py"])
        except Exception as e:
            print(f"Failed to launch Sheets: {e}")
    def launch_mines(self):
        try:
            subprocess.Popen([sys.executable, "Applications/games/mines.py"])
        except Exception as e:
            print(f"Failed to launch Mines: {e}")
    def launch_tetris(self):
            try:
                subprocess.Popen([sys.executable, "Applications/games/tetris.py"])
            except Exception as e:
                print(f"Failed to launch Tetris: {e}")
    def launch_shop(self):
        try:
            subprocess.Popen([sys.executable, "Applications/store.py"])
        except Exception as e:
            print(f"Failed to launch Franny's Pop Shop: {e}")
    def launch_calc(self):
        try:
            subprocess.Popen([sys.executable, "Applications/calculator.py"])
        except Exception as e:
            print(f"Failed to launch Calculator: {e}")
    def launch_note(self):
        try:
            subprocess.Popen([sys.executable, "Applications/notetaking.py"])
        except Exception as e:
            print(f"Failed to launch Note: {e}")
    def launch_tempo(self):
        try:
            subprocess.Popen([sys.executable, "Applications/tempo.py"])
        except Exception as e:
            print(f"Failed to launch Tempo: {e}")
    def launch_email(self):
        try:
            subprocess.Popen([sys.executable, "Applications/franmail.py"])
        except Exception as e:
            print(f"Failed to launch Franmail: {e}")
    def launch_runner(self):
        try:
            subprocess.Popen([sys.executable, "Applications/games/runner.py"])
        except Exception as e:
            print(f"Failed to launch Runner: {e}")
if __name__ == "__main__":
    taskbar = Taskbar()
    taskbar.mainloop()
