# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ExifTags


class ImageViewer:
    def __init__(self):
        self.root = tk.Toplevel()
        self.root.title("Outsider v1.14")
        self.root.geometry("800x600")
        self.root.configure(bg="black")
        self.root.bind("<Control-w>", lambda e: self.root.destroy())

        self.image_label = tk.Label(self.root, bg="black")
        self.image_label.pack(expand=True)
        self.image_label.bind("<Button-3>", self.show_metadata)

        self.image_label.drop_target_register(tk.DND_FILES)
        self.image_label.dnd_bind("<<Drop>>", self.on_drop)

        self.toolbar = tk.Frame(self.root, bg="gray")
        self.toolbar.pack(side="bottom", fill="x")

        tk.Button(self.toolbar, text="Open", command=self.open_image).pack(side="left")
        tk.Button(self.toolbar, text="Previous", command=self.show_previous).pack(side="left")
        tk.Button(self.toolbar, text="Next", command=self.show_next).pack(side="left")
        tk.Button(self.toolbar, text="Zoom In", command=self.zoom_in).pack(side="left")
        tk.Button(self.toolbar, text="Zoom Out", command=self.zoom_out).pack(side="left")
        tk.Button(self.toolbar, text="Rotate right", command=self.rotate_right).pack(side="left")
        tk.Button(self.toolbar, text="Rotate left", command=self.rotate_left).pack(side="left")
        tk.Button(self.toolbar, text="Slideshow", command=self.toggle_slideshow).pack(side="left")
        tk.Button(self.toolbar, text="Fullscreen", command=self.toggle_fullscreen).pack(side="left")

        self.image_paths = []
        self.current_index = 0
        self.original_image = None
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.fullscreen = False
        self.slideshow_running = False

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
        )
        if file_path:
            self.load_image_group(file_path)

    def load_image_group(self, file_path):
        directory = os.path.dirname(file_path)
        self.image_paths = [
            os.path.join(directory, f)
            for f in os.listdir(directory)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]
        self.image_paths.sort()
        self.current_index = self.image_paths.index(file_path)
        self.load_image(file_path)

    def load_image(self, path):
        self.original_image = Image.open(path)
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.display_image()

    def display_image(self):
        if self.original_image:
            w, h = self.original_image.size
            resized = self.original_image.resize(
                (int(w * self.zoom_factor), int(h * self.zoom_factor)), Image.ANTIALIAS
            )
            rotated = resized.rotate(self.rotation_angle, expand=True)
            self.tk_image = ImageTk.PhotoImage(rotated)
            self.image_label.configure(image=self.tk_image)

    def show_previous(self):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.load_image(self.image_paths[self.current_index])

    def show_next(self):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.load_image(self.image_paths[self.current_index])

    def zoom_in(self):
        self.zoom_factor *= 1.25
        self.display_image()

    def zoom_out(self):
        self.zoom_factor /= 1.25
        self.display_image()

    def rotate_right(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.display_image()

    def rotate_left(self):
        self.rotation_angle = (self.rotation_angle - 90) % 360
        self.display_image()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)

    def toggle_slideshow(self):
        self.slideshow_running = not self.slideshow_running
        if self.slideshow_running:
            self.run_slideshow()

    def run_slideshow(self):
        def loop():
            while self.slideshow_running:
                self.show_next()
                self.root.after(3000)
                if not self.slideshow_running:
                    break
        threading.Thread(target=loop, daemon=True).start()

    def show_metadata(self, event=None):
        if not self.original_image:
            return
        try:
            exif = self.original_image._getexif()
            if not exif:
                messagebox.showinfo("Metadata", "No EXIF metadata found.")
                return
            exif_data = {
                ExifTags.TAGS.get(k, str(k)): str(v)
                for k, v in exif.items()
            }
            info = "\n".join(f"{k}: {v}" for k, v in exif_data.items())
            messagebox.showinfo("Image Metadata", info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read metadata:\n{e}")

    def on_drop(self, event):
        file_path = event.data.strip()
        if os.path.isfile(file_path):
            self.load_image_group(file_path)

def launch():
    ImageViewer()
