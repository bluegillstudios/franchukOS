# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.


import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class TaskManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Task Manager")
        self.root.geometry("800x600")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.setup_cpu_tab()
        self.setup_memory_tab()
        self.setup_process_tab()
        self.setup_network_tab()
        self.setup_disk_tab()

        self.update_data()

    def setup_cpu_tab(self):
        self.cpu_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cpu_frame, text="CPU")
        self.cpu_label = ttk.Label(self.cpu_frame, text="Loading CPU usage...")
        self.cpu_label.pack(pady=10)

        self.cpu_fig = Figure(figsize=(5, 3), dpi=100)
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_usage_line, = self.cpu_ax.plot([], [], label="CPU Usage (%)")
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.set_title("CPU Usage")
        self.cpu_ax.set_xlabel("Time (s)")
        self.cpu_ax.set_ylabel("Usage (%)")

        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, master=self.cpu_frame)
        self.cpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.cpu_data = []

    def setup_memory_tab(self):
        self.memory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.memory_frame, text="Memory")
        self.memory_label = ttk.Label(self.memory_frame, text="Loading memory usage...")
        self.memory_label.pack(pady=10)

    def setup_process_tab(self):
        self.process_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.process_frame, text="Processes")
        self.process_tree = ttk.Treeview(self.process_frame, columns=("PID", "Name", "CPU", "Memory"), show='headings')
        self.process_tree.heading("PID", text="PID")
        self.process_tree.heading("Name", text="Name")
        self.process_tree.heading("CPU", text="CPU (%)")
        self.process_tree.heading("Memory", text="Memory (%)")
        self.process_tree.pack(fill=tk.BOTH, expand=True)

    def setup_network_tab(self):
        self.network_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.network_frame, text="Network")
        self.network_label = ttk.Label(self.network_frame, text="Loading network usage...")
        self.network_label.pack(pady=10)

    def setup_disk_tab(self):
        self.disk_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.disk_frame, text="Disk")
        self.disk_label = ttk.Label(self.disk_frame, text="Loading disk usage...")
        self.disk_label.pack(pady=10)

    def update_data(self):
        # CPU
        cpu_percent = psutil.cpu_percent()
        self.cpu_label.config(text=f"CPU Usage: {cpu_percent}%")
        self.cpu_data.append(cpu_percent)
        if len(self.cpu_data) > 60:
            self.cpu_data.pop(0)
        self.cpu_usage_line.set_data(range(len(self.cpu_data)), self.cpu_data)
        self.cpu_ax.set_xlim(0, max(60, len(self.cpu_data)))
        self.cpu_canvas.draw()

        # Memory
        mem = psutil.virtual_memory()
        self.memory_label.config(text=f"Memory Usage: {mem.percent}% ({mem.used // (1024 ** 2)}MB / {mem.total // (1024 ** 2)}MB)")

        # Processes
        for row in self.process_tree.get_children():
            self.process_tree.delete(row)
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            self.process_tree.insert('', tk.END, values=(
                proc.info['pid'], proc.info['name'], f"{proc.info['cpu_percent']:.1f}", f"{proc.info['memory_percent']:.1f}"
            ))

        # Network
        net = psutil.net_io_counters()
        self.network_label.config(text=f"Sent: {net.bytes_sent // (1024 ** 2)} MB | Received: {net.bytes_recv // (1024 ** 2)} MB")

        # Disk
        disk = psutil.disk_usage('/')
        self.disk_label.config(text=f"Disk Usage: {disk.percent}% ({disk.used // (1024 ** 3)}GB / {disk.total // (1024 ** 3)}GB)")

        self.root.after(1000, self.update_data)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = TaskManager()
    app.run()