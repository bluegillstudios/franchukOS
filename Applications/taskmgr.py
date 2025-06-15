# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.


import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time
from collections import deque
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class TaskManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Task Manager")
        self.root.geometry("900x650")
        self.root.configure(bg="#23272e")

        # Modern ttk theme
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('.', font=('Segoe UI', 11))
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 10))
        style.configure('TNotebook.Tab', padding=[12, 8], font=('Segoe UI', 11, 'bold'))
        style.map('Treeview', background=[('selected', '#0078d7')])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.setup_cpu_tab()
        self.setup_memory_tab()
        self.setup_process_tab()
        self.setup_network_tab()
        self.setup_disk_tab()

        self.cpu_data = deque(maxlen=60)
        self.last_process_update = 0

        self.update_data()

    def setup_cpu_tab(self):
        self.cpu_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.cpu_frame, text="CPU")

        self.cpu_label = ttk.Label(self.cpu_frame, text="CPU Usage:", font=('Segoe UI', 12, 'bold'))
        self.cpu_label.pack(pady=(10, 2))

        self.cpu_progress = ttk.Progressbar(self.cpu_frame, orient='horizontal', length=400, mode='determinate')
        self.cpu_progress.pack(pady=(0, 10))

        self.cpu_fig = Figure(figsize=(5, 2.5), dpi=100)
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_usage_line, = self.cpu_ax.plot([], [], label="CPU Usage (%)", color='#0078d7')
        self.cpu_ax.set_ylim(0, 100)
        self.cpu_ax.set_xlim(0, 60)
        self.cpu_ax.set_title("CPU Usage (Last 60s)")
        self.cpu_ax.set_xlabel("Time (s)")
        self.cpu_ax.set_ylabel("Usage (%)")
        self.cpu_ax.grid(True, linestyle='--', alpha=0.5)
        self.cpu_ax.legend(loc='upper right')

        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, master=self.cpu_frame)
        self.cpu_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_memory_tab(self):
        self.memory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.memory_frame, text="Memory")

        self.memory_label = ttk.Label(self.memory_frame, text="Memory Usage:", font=('Segoe UI', 12, 'bold'))
        self.memory_label.pack(pady=(10, 2))

        self.memory_progress = ttk.Progressbar(self.memory_frame, orient='horizontal', length=400, mode='determinate')
        self.memory_progress.pack(pady=(0, 10))

    def setup_process_tab(self):
        self.process_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.process_frame, text="Processes")

        columns = ("PID", "Name", "CPU", "Memory")
        self.process_tree = ttk.Treeview(self.process_frame, columns=columns, show='headings', selectmode='browse')
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, anchor='center', width=120 if col != "Name" else 260)
        self.process_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Add striped rows
        self.process_tree.tag_configure('oddrow', background='#f0f4fa')
        self.process_tree.tag_configure('evenrow', background='#e3eaf2')

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(self.process_frame, orient="vertical", command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')

    def setup_network_tab(self):
        self.network_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.network_frame, text="Network")
        self.network_label = ttk.Label(self.network_frame, text="Loading network usage...", font=('Segoe UI', 12, 'bold'))
        self.network_label.pack(pady=10)

    def setup_disk_tab(self):
        self.disk_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.disk_frame, text="Disk")
        self.disk_label = ttk.Label(self.disk_frame, text="Loading disk usage...", font=('Segoe UI', 12, 'bold'))
        self.disk_label.pack(pady=10)

    def update_data(self):
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        self.cpu_label.config(text=f"CPU Usage: {cpu_percent:.1f}%")
        self.cpu_progress['value'] = cpu_percent
        self.cpu_data.append(cpu_percent)
        self.cpu_usage_line.set_data(range(len(self.cpu_data)), list(self.cpu_data))
        self.cpu_ax.set_xlim(0, 60)
        self.cpu_canvas.draw_idle()

        # Memory
        mem = psutil.virtual_memory()
        self.memory_label.config(text=f"Memory Usage: {mem.percent:.1f}% ({mem.used // (1024 ** 2)}MB / {mem.total // (1024 ** 2)}MB)")
        self.memory_progress['value'] = mem.percent

        # Processes (update every 2 seconds)
        now = time.time()
        if now - self.last_process_update > 2:
            for row in self.process_tree.get_children():
                self.process_tree.delete(row)
            for i, proc in enumerate(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])):
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                try:
                    self.process_tree.insert('', tk.END, values=(
                        proc.info['pid'],
                        proc.info['name'][:32],
                        f"{proc.info['cpu_percent']:.1f}",
                        f"{proc.info['memory_percent']:.1f}"
                    ), tags=(tag,))
                except Exception:
                    continue
            self.last_process_update = now

        # Network
        net = psutil.net_io_counters()
        self.network_label.config(text=f"Sent: {net.bytes_sent // (1024 ** 2)} MB | Received: {net.bytes_recv // (1024 ** 2)} MB")

        # Disk
        disk = psutil.disk_usage('/')
        self.disk_label.config(text=f"Disk Usage: {disk.percent:.1f}% ({disk.used // (1024 ** 3)}GB / {disk.total // (1024 ** 3)}GB)")

        self.root.after_idle(lambda: self.root.after(1000, self.update_data))

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = TaskManager()
    app.run()