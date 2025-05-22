# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ExifTags, ImageEnhance, ImageOps
from tkinterdnd2 import DND_FILES, TkinterDnD
import playsound

BUTTON_STYLE = {
    "bg": "#222",
    "fg": "#eee",
    "activebackground": "#444",
    "activeforeground": "#fff",
    "relief": tk.FLAT,
    "bd": 0,
    "padx": 10,
    "pady": 5
}


class Outsider:
    def __init__(self, parent=None):
        if parent is None:
            self.root = TkinterDnD.Tk()
            enable_dnd = True
        else:
            self.root = tk.Toplevel(parent)
            enable_dnd = False

        self.root.title("Outsider v1.87")
        self.root.geometry("1000x700")
        self.root.configure(bg="#111")
        self.root.bind("<Control-w>", lambda e: self.root.destroy())

        self.image_frame = tk.Frame(self.root, bg="#111", bd=2)
        self.image_frame.pack(expand=True, fill="both", padx=8, pady=8)

        self.image_label = tk.Label(self.image_frame, bg="#111")
        self.image_label.pack(expand=True, fill="both")
        self.image_label.bind("<Button-3>", self.show_metadata)

        if enable_dnd:
            self.image_label.drop_target_register(DND_FILES)
            self.image_label.dnd_bind("<<Drop>>", self.on_drop)

        self.build_toolbar()

        self.image_paths = []
        self.current_index = 0
        self.original_image = None
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.fullscreen = False
        self.slideshow_running = False

    def build_toolbar(self):
        toolbar = tk.Frame(self.root, bg="#222", pady=5)
        toolbar.pack(side="top", fill="x")

        def add_button(text, cmd):
            return tk.Button(toolbar, text=text, command=cmd, **BUTTON_STYLE).pack(side="left", padx=4)

        add_button("📂 Open", self.open_image)
        add_button("⬅ Previous", self.show_previous)
        add_button("➡ Next", self.show_next)
        add_button("➕ Zoom In", self.zoom_in)
        add_button("➖ Zoom Out", self.zoom_out)
        add_button("🔄 Rotate →", self.rotate_right)
        add_button("↩ Rotate ←", self.rotate_left)
        add_button("▶ Slideshow", self.toggle_slideshow)
        add_button("🖥 Fullscreen", self.toggle_fullscreen)

        # Editing tools
        add_button("↔ Flip H", self.flip_horizontal)
        add_button("↕ Flip V", self.flip_vertical)
        add_button("🌑 Grayscale", self.apply_grayscale)
        add_button("☀+", lambda: self.adjust_brightness(1.2))
        add_button("☀-", lambda: self.adjust_brightness(0.8))
        add_button("🎚+", lambda: self.adjust_contrast(1.2))
        add_button("🎚-", lambda: self.adjust_contrast(0.8))
        add_button("🎨 Sepia", self.apply_sepia_filter)

        tip = tk.Label(self.root, text="Right-click for metadata | Ctrl+W to close", bg="#111", fg="#555", font=("Arial", 9))
        tip.pack(side="bottom", pady=4)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")],
            parent=self.root
        )
        if file_path:
            self.load_image_group(file_path)

    def load_image_group(self, file_path):
        directory = os.path.dirname(file_path)
        self.image_paths = [
            os.path.abspath(os.path.join(directory, f))
            for f in os.listdir(directory)
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
        ]
        self.image_paths.sort()
        abs_file_path = os.path.abspath(file_path)
        if abs_file_path in self.image_paths:
            self.current_index = self.image_paths.index(abs_file_path)
            self.load_image(abs_file_path)
        else:
            messagebox.showerror("Error", f"Selected file is not a supported image:\n{abs_file_path}")
            playsound.playsound("assets/sounds/error.wav")

    def load_image(self, path):
        try:
            self.original_image = Image.open(path).convert("RGB")
            self.zoom_factor = 1.0
            self.rotation_angle = 0
            self.display_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def display_image(self):
        if self.original_image:
            w, h = self.original_image.size
            resized = self.original_image.resize(
                (int(w * self.zoom_factor), int(h * self.zoom_factor)), Image.LANCZOS
            )
            rotated = resized.rotate(self.rotation_angle, expand=True)
            self.tk_image = ImageTk.PhotoImage(rotated)
            self.image_label.configure(image=self.tk_image)
            self.image_label.image = self.tk_image

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
        if self.slideshow_running:
            self.show_next()
            self.root.after(3000, self.run_slideshow)

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

    def flip_horizontal(self):
        if self.original_image:
            self.original_image = self.original_image.transpose(Image.FLIP_LEFT_RIGHT)
            self.display_image()

    def flip_vertical(self):
        if self.original_image:
            self.original_image = self.original_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.display_image()

    def apply_grayscale(self):
        if self.original_image:
            self.original_image = ImageOps.grayscale(self.original_image).convert("RGB")
            self.display_image()

    def adjust_brightness(self, factor):
        if self.original_image:
            enhancer = ImageEnhance.Brightness(self.original_image)
            self.original_image = enhancer.enhance(factor)
            self.display_image()

    def adjust_contrast(self, factor):
        if self.original_image:
            enhancer = ImageEnhance.Contrast(self.original_image)
            self.original_image = enhancer.enhance(factor)
            self.display_image()

    def apply_sepia_filter(self):
        if self.original_image:
            img = self.original_image.convert("RGB")
            pixels = img.load()
            for y in range(img.height):
                for x in range(img.width):
                    r, g, b = pixels[x, y]
                    tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                    tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                    tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                    pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
            self.original_image = img
            self.display_image()

    def on_drop(self, event):
        file_path = event.data.strip()
        if os.path.isfile(file_path):
            self.load_image_group(file_path)

def launch():
    Outsider()
