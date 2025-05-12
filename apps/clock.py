# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import messagebox
import time
import threading
import winsound  
import playsound 

class ClockApp:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="black")

        # Clock Label
        self.clock_label = tk.Label(self.root, text="", font=("Helvetica", 40), fg="white", bg="black")
        self.clock_label.pack(pady=20)

        # Stopwatch components
        self.stopwatch_label = tk.Label(self.root, text="Stopwatch: 00:00", font=("Helvetica", 15), fg="white", bg="black")
        self.stopwatch_label.pack(pady=10)
        self.stopwatch_start_time = 0
        self.stopwatch_running = False
        self.stopwatch_elapsed = 0
        self.stopwatch_button = tk.Button(self.root, text="Start", command=self.toggle_stopwatch, bg="gray")
        self.stopwatch_button.pack()

        # Timer components
        self.timer_label = tk.Label(self.root, text="Timer: 00:00", font=("Helvetica", 15), fg="white", bg="black")
        self.timer_label.pack(pady=10)
        self.timer_running = False
        self.timer_seconds = 0
        self.timer_entry = tk.Entry(self.root, width=10, font=("Helvetica", 14))
        self.timer_entry.pack(pady=5)
        self.timer_button = tk.Button(self.root, text="Set Timer", command=self.set_timer, bg="gray")
        self.timer_button.pack()

        # Alarm components
        self.alarm_label = tk.Label(self.root, text="Set Alarm (HH:MM):", font=("Helvetica", 15), fg="white", bg="black")
        self.alarm_label.pack(pady=10)
        self.alarm_entry = tk.Entry(self.root, width=10, font=("Helvetica", 14))
        self.alarm_entry.pack(pady=5)
        self.alarm_button = tk.Button(self.root, text="Set Alarm", command=self.set_alarm, bg="gray")
        self.alarm_button.pack()

        # Update clock every second
        self.update_clock()

    def update_clock(self):
        """Update the clock label every second."""
        current_time = time.strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)

    def toggle_stopwatch(self):
        """Start/Stop the stopwatch."""
        if self.stopwatch_running:
            self.stopwatch_running = False
            self.stopwatch_button.config(text="Start")
        else:
            self.stopwatch_start_time = time.time() - self.stopwatch_elapsed
            self.stopwatch_running = True
            self.stopwatch_button.config(text="Stop")
            self.update_stopwatch()

    def update_stopwatch(self):
        """Update the stopwatch time."""
        if self.stopwatch_running:
            self.stopwatch_elapsed = time.time() - self.stopwatch_start_time
            minutes = int(self.stopwatch_elapsed // 60)
            seconds = int(self.stopwatch_elapsed % 60)
            self.stopwatch_label.config(text=f"Stopwatch: {minutes:02}:{seconds:02}")
            self.root.after(100, self.update_stopwatch)

    def set_timer(self):
        """Set the timer based on user input."""
        try:
            self.timer_seconds = int(self.timer_entry.get()) * 60
            self.timer_running = True
            self.start_timer()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")

    def start_timer(self):
        """Start the countdown timer."""
        if self.timer_running and self.timer_seconds > 0:
            minutes = self.timer_seconds // 60
            seconds = self.timer_seconds % 60
            self.timer_label.config(text=f"Timer: {minutes:02}:{seconds:02}")
            self.timer_seconds -= 1
            self.root.after(1000, self.start_timer)
        elif self.timer_seconds == 0:
            self.timer_label.config(text="Timer: 00:00")
            self.timer_running = False
            self.timer_alert()

    def timer_alert(self):
        """Alert the user when the timer reaches zero."""
        messagebox.showinfo("Timer", "Time's up!")
        winsound.Beep(1000, 1000)  

    def set_alarm(self):
        """Set an alarm based on user input."""
        alarm_time = self.alarm_entry.get()
        try:
            alarm_hours, alarm_minutes = map(int, alarm_time.split(":"))
            alarm_seconds = alarm_hours * 3600 + alarm_minutes * 60
            threading.Thread(target=self.check_alarm, args=(alarm_seconds,), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid alarm time (HH:MM).")

    def check_alarm(self, alarm_seconds):
        """Check if the current time matches the alarm time."""
        while True:
            current_seconds = time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec
            if current_seconds == alarm_seconds:
                self.alarm_trigger()
                break
            time.sleep(1)

    def alarm_trigger(self):
        """Trigger the alarm sound."""
        messagebox.showinfo("Alarm", "It's time!")
        winsound.Beep(1500, 1000)  # Windows
        playsound.playsound("wake.mp3") # linux or anything else idgaf 

if __name__ == "__main__":
    root = tk.Tk()
    app = ClockApp(root)
    root.mainloop()
