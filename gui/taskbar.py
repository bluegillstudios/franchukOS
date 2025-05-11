# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import messagebox
import time
from threading import Thread
from datetime import datetime
from apps.file_explorer import FileExplorer
from apps.terminal import Terminal

class WindowManager:
    def __init__(self, taskbar):
        self.taskbar = taskbar
        self.open_windows = {}
        self.active_window = None

    def open_window(self, window_name, window_class):
        if window_name not in self.open_windows:
            window = window_class(self.taskbar, window_name, self)
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
        if self.active_window:
            self.active_window.withdraw()

        # Show the new window and make it active
        self.active_window = self.open_windows[window_name]
        self.active_window.deiconify()  # Show the window again
        self.taskbar.update_taskbar_button(window_name)  # Update taskbar to show active window

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

class Taskbar(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FranchukOS Taskbar")
        self.geometry("800x50")
        self.configure(bg="black")

        self.window_manager = WindowManager(self)

        self.taskbar_frame = tk.Frame(self, bg="black", height=50)
        self.taskbar_frame.pack(fill="x", side="bottom")

        self.start_button = tk.Button(self.taskbar_frame, text="Start", command=self.show_start_menu, bg="black", fg="lime", font=("Courier", 12))
        self.start_button.pack(side="left", padx=5)

        self.clock_label = tk.Label(self.taskbar_frame, text=self.get_time(), bg="black", fg="lime", font=("Courier", 12))
        self.clock_label.pack(side="right", padx=10)

        self.update_time_thread = Thread(target=self.update_time, daemon=True)
        self.update_time_thread.start()

        self.system_tray = tk.Frame(self.taskbar_frame, bg="black")
        self.system_tray.pack(side="right", padx=10)

        self.taskbar_buttons_frame = tk.Frame(self, bg="black")
        self.taskbar_buttons_frame.pack(side="bottom", fill="x")

    def get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def update_time(self):
        while True:
            time.sleep(1)
            self.clock_label.config(text=self.get_time())

    def show_start_menu(self):
        menu = tk.Menu(self, tearoff=0, bg="black", fg="lime")
        menu.add_command(label="File Explorer", command=self.launch_file_explorer)
        menu.add_command(label="Terminal", command=self.launch_terminal)
        menu.add_separator()
        menu.add_command(label="Exit", command=self.exit_os)

        menu.post(self.winfo_rootx() + self.start_button.winfo_x(), self.winfo_rooty() + self.start_button.winfo_y() + 50)

    def exit_os(self):
        confirm = messagebox.askyesno("Exit", "Are you sure you want to exit FranchukOS?")
        if confirm:
            self.quit()

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

    def launch_file_explorer(self):
        self.window_manager.open_window("File Explorer", FileExplorer)

    def launch_terminal(self):
        self.window_manager.open_window("Terminal", Terminal)

if __name__ == "__main__":
    taskbar = Taskbar()
    taskbar.mainloop()
