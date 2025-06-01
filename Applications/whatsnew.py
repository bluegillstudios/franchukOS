import tkinter as tk
from tkinter import ttk
import json
import os

UPDATE_FILE = "updates.json"

def load_updates():
    if os.path.exists(UPDATE_FILE):
        with open(UPDATE_FILE, "r") as f:
            return json.load(f)
    else:
        return [
            {"title": "Welcome to franchukOS!", "description": "32 versions and counting!"},
            {"title": "New App: What's New", "description": "Stay informed with the latest updates and features!"},
            {"title": "Version 32.0 is now out", "description": (
                "- Added color themes to Terminal\n"
                "- Added Boardroom: a calendar, reminding, and scheduling app\n"
                "- Added Shelf: offline ebook and document reader\n"
                "- Updated Franny to v16"
            )}
        ]

class WhatsNewApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("What's New")
        self.geometry("400x500")
        self.configure(bg="#f4f4f4")

        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self, text="What's New", font=("Helvetica", 16, "bold"), bg="#f4f4f4")
        label.pack(pady=10)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="#f4f4f4")
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f4f4f4")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for update in load_updates():
            title = tk.Label(scrollable_frame, text=update["title"], font=("Helvetica", 12, "bold"), bg="#f4f4f4")
            desc = tk.Label(scrollable_frame, text=update["description"], wraplength=350, justify="left", bg="#f4f4f4")
            title.pack(anchor="w", padx=10, pady=(10, 0))
            desc.pack(anchor="w", padx=10, pady=(0, 10))

        exit_button = ttk.Button(self, text="Close", command=self.destroy)
        exit_button.pack(pady=10)

if __name__ == "__main__":
    app = WhatsNewApp()
    app.mainloop()
