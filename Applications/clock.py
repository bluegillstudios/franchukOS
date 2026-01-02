# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import messagebox, ttk, colorchooser, simpledialog
import time
import datetime

class ClockApp(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Clock")
        self.geometry("400x500")
        self.resizable(False, False)
        self.configure(bg="#181818")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Theme colors
        self.fg_color = "#ffffff"
        self.bg_color = "#181818"
        self.accent_color = "#00bfff"

        # Clock Label
        self.clock_label = tk.Label(self, text="", font=("Consolas", 48, "bold"), fg=self.fg_color, bg=self.bg_color)
        self.clock_label.pack(pady=20)

        # Date Label
        self.date_label = tk.Label(self, text="", font=("Consolas", 18), fg=self.fg_color, bg=self.bg_color)
        self.date_label.pack(pady=5)

        # Tabs for Stopwatch, Timer, Alarm, World Clock
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=True, fill="both", padx=10, pady=10)

        # Stopwatch Tab
        self.stopwatch_tab = tk.Frame(self.tabs, bg=self.bg_color)
        self.tabs.add(self.stopwatch_tab, text="Stopwatch")
        self.init_stopwatch_tab()

        # Timer Tab
        self.timer_tab = tk.Frame(self.tabs, bg=self.bg_color)
        self.tabs.add(self.timer_tab, text="Timer")
        self.init_timer_tab()

        # Alarm Tab
        self.alarm_tab = tk.Frame(self.tabs, bg=self.bg_color)
        self.tabs.add(self.alarm_tab, text="Alarm")
        self.init_alarm_tab()

        # World Clock Tab
        self.world_tab = tk.Frame(self.tabs, bg=self.bg_color)
        self.tabs.add(self.world_tab, text="World Clock")
        self.init_world_tab()

        # Settings Button
        self.settings_btn = tk.Button(self, text="⚙️ Settings", command=self.open_settings, bg=self.bg_color, fg=self.fg_color, borderwidth=0, font=("Arial", 12))
        self.settings_btn.pack(pady=5, anchor="ne", padx=10)

        self.update_clock()

    def on_close(self):
        self.destroy()

    # --- CLOCK & DATE ---
    def update_clock(self):
        now = datetime.datetime.now()
        self.clock_label.config(text=now.strftime("%H:%M:%S"))
        self.date_label.config(text=now.strftime("%A, %B %d, %Y"))
        self.after(1000, self.update_clock)

    # --- STOPWATCH ---
    def init_stopwatch_tab(self):
        self.stopwatch_label = tk.Label(self.stopwatch_tab, text="00:00:00", font=("Consolas", 32), fg=self.fg_color, bg=self.bg_color)
        self.stopwatch_label.pack(pady=20)
        self.stopwatch_running = False
        self.stopwatch_start_time = 0
        self.stopwatch_elapsed = 0

        btn_frame = tk.Frame(self.stopwatch_tab, bg=self.bg_color)
        btn_frame.pack(pady=10)
        self.stop_btn = tk.Button(btn_frame, text="Start", command=self.toggle_stopwatch, width=8, bg=self.accent_color, fg="white")
        self.stop_btn.grid(row=0, column=0, padx=5)
        self.reset_btn = tk.Button(btn_frame, text="Reset", command=self.reset_stopwatch, width=8, bg="#444", fg="white")
        self.reset_btn.grid(row=0, column=1, padx=5)

        self.lap_list = tk.Listbox(self.stopwatch_tab, font=("Consolas", 12), height=5, bg="#222", fg=self.fg_color)
        self.lap_list.pack(pady=5, fill="x", padx=20)
        self.lap_btn = tk.Button(self.stopwatch_tab, text="Lap", command=self.add_lap, width=8, bg="#444", fg="white")
        self.lap_btn.pack(pady=2)

    def toggle_stopwatch(self):
        if self.stopwatch_running:
            self.stopwatch_running = False
            self.stop_btn.config(text="Start")
        else:
            self.stopwatch_start_time = time.time() - self.stopwatch_elapsed
            self.stopwatch_running = True
            self.stop_btn.config(text="Stop")
            self.update_stopwatch()

    def update_stopwatch(self):
        if self.stopwatch_running:
            self.stopwatch_elapsed = time.time() - self.stopwatch_start_time
            h = int(self.stopwatch_elapsed // 3600)
            m = int((self.stopwatch_elapsed % 3600) // 60)
            s = int(self.stopwatch_elapsed % 60)
            self.stopwatch_label.config(text=f"{h:02}:{m:02}:{s:02}")
            self.after(100, self.update_stopwatch)

    def reset_stopwatch(self):
        self.stopwatch_running = False
        self.stopwatch_elapsed = 0
        self.stop_btn.config(text="Start")
        self.stopwatch_label.config(text="00:00:00")
        self.lap_list.delete(0, tk.END)

    def add_lap(self):
        if self.stopwatch_running:
            h = int(self.stopwatch_elapsed // 3600)
            m = int((self.stopwatch_elapsed % 3600) // 60)
            s = int(self.stopwatch_elapsed % 60)
            self.lap_list.insert(tk.END, f"{h:02}:{m:02}:{s:02}")

    # --- TIMER ---
    def init_timer_tab(self):
        self.timer_label = tk.Label(self.timer_tab, text="00:00:00", font=("Consolas", 32), fg=self.fg_color, bg=self.bg_color)
        self.timer_label.pack(pady=20)
        self.timer_entry = tk.Entry(self.timer_tab, width=10, font=("Consolas", 16))
        self.timer_entry.pack(pady=5)
        self.timer_entry.insert(0, "5")  # default 5 minutes
        self.timer_running = False
        self.timer_seconds = 0

        btn_frame = tk.Frame(self.timer_tab, bg=self.bg_color)
        btn_frame.pack(pady=10)
        self.set_timer_btn = tk.Button(btn_frame, text="Set Timer", command=self.set_timer, width=10, bg=self.accent_color, fg="white")
        self.set_timer_btn.grid(row=0, column=0, padx=5)
        self.cancel_timer_btn = tk.Button(btn_frame, text="Cancel", command=self.cancel_timer, width=10, bg="#444", fg="white")
        self.cancel_timer_btn.grid(row=0, column=1, padx=5)

    def set_timer(self):
        try:
            mins = int(self.timer_entry.get())
            self.timer_seconds = mins * 60
            self.timer_running = True
            self.update_timer()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def update_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            h = self.timer_seconds // 3600
            m = (self.timer_seconds % 3600) // 60
            s = self.timer_seconds % 60
            self.timer_label.config(text=f"{h:02}:{m:02}:{s:02}")
            self.timer_seconds -= 1
            self.after(1000, self.update_timer)
        elif self.timer_running and self.timer_seconds == 0:
            self.timer_label.config(text="00:00:00")
            self.timer_running = False
            messagebox.showinfo("Timer", "Time's up!")

    def cancel_timer(self):
        self.timer_running = False
        self.timer_label.config(text="00:00:00")

    # --- ALARM ---
    def init_alarm_tab(self):
        self.alarm_list = tk.Listbox(self.alarm_tab, font=("Consolas", 12), height=5, bg="#222", fg=self.fg_color)
        self.alarm_list.pack(pady=10, fill="x", padx=20)
        btn_frame = tk.Frame(self.alarm_tab, bg=self.bg_color)
        btn_frame.pack(pady=5)
        self.add_alarm_btn = tk.Button(btn_frame, text="Add Alarm", command=self.add_alarm, width=10, bg=self.accent_color, fg="white")
        self.add_alarm_btn.grid(row=0, column=0, padx=5)
        self.remove_alarm_btn = tk.Button(btn_frame, text="Remove", command=self.remove_alarm, width=10, bg="#444", fg="white")
        self.remove_alarm_btn.grid(row=0, column=1, padx=5)
        self.alarms = []
        self.check_alarms()

    def add_alarm(self):
        alarm_time = simpledialog.askstring("Set Alarm", "Enter time (HH:MM):", parent=self)
        if alarm_time:
            try:
                h, m = map(int, alarm_time.split(":"))
                if 0 <= h < 24 and 0 <= m < 60:
                    self.alarms.append(alarm_time)
                    self.alarm_list.insert(tk.END, alarm_time)
                else:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid time (HH:MM).")

    def remove_alarm(self):
        sel = self.alarm_list.curselection()
        if sel:
            idx = sel[0]
            self.alarm_list.delete(idx)
            del self.alarms[idx]

    def check_alarms(self):
        now = datetime.datetime.now().strftime("%H:%M")
        if now in self.alarms:
            self.alarms.remove(now)
            self.alarm_list.delete(0, tk.END)
            for alarm in self.alarms:
                self.alarm_list.insert(tk.END, alarm)
            messagebox.showinfo("Alarm", "It's time!")
        self.after(1000 * 30, self.check_alarms)

    # --- WORLD CLOCK ---
    def init_world_tab(self):
        self.world_list = tk.Listbox(self.world_tab, font=("Consolas", 12), height=8, bg="#222", fg=self.fg_color)
        self.world_list.pack(pady=10, fill="x", padx=20)
        btn_frame = tk.Frame(self.world_tab, bg=self.bg_color)
        btn_frame.pack(pady=5)
        self.add_city_btn = tk.Button(btn_frame, text="Add City", command=self.add_city, width=10, bg=self.accent_color, fg="white")
        self.add_city_btn.grid(row=0, column=0, padx=5)
        self.remove_city_btn = tk.Button(btn_frame, text="Remove", command=self.remove_city, width=10, bg="#444", fg="white")
        self.remove_city_btn.grid(row=0, column=1, padx=5)
        self.cities = []
        self.update_world_clock()

    def add_city(self):
        city = simpledialog.askstring("Add City", "Enter city (e.g. London, Tokyo):", parent=self)
        if city:
            self.cities.append(city)
            self.world_list.insert(tk.END, f"{city}: ...")

    def remove_city(self):
        sel = self.world_list.curselection()
        if sel:
            idx = sel[0]
            self.world_list.delete(idx)
            del self.cities[idx]

    def update_world_clock(self):
        self.world_list.delete(0, tk.END)
        self.world_list.insert(tk.END, f"Local: {datetime.datetime.now().strftime('%H:%M:%S')}")
        self.world_list.insert(tk.END, f"UTC:   {datetime.datetime.utcnow().strftime('%H:%M:%S')}")
        for city in self.cities:
            self.world_list.insert(tk.END, f"{city}: ...")
        self.after(1000, self.update_world_clock)

    # --- SETTINGS ---
    def open_settings(self):
        dialog = tk.Toplevel(self)
        dialog.title("Clock Settings")
        dialog.geometry("300x200")
        dialog.configure(bg=self.bg_color)

        def set_theme():
            color = colorchooser.askcolor(title="Choose Background Color")[1]
            if color:
                self.bg_color = color
                self.configure(bg=color)
                self.clock_label.config(bg=color)
                self.date_label.config(bg=color)
                for tab in [self.stopwatch_tab, self.timer_tab, self.alarm_tab, self.world_tab]:
                    tab.config(bg=color)

        theme_btn = tk.Button(dialog, text="Change Theme Color", command=set_theme, bg=self.accent_color, fg="white")
        theme_btn.pack(pady=20)

        close_btn = tk.Button(dialog, text="Close", command=dialog.destroy, bg="#444", fg="white")
        close_btn.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide root
    app = ClockApp(root)
    app.mainloop()
