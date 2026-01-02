# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ExifTags, ImageEnhance, ImageOps
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_TKINTERDND = True
except Exception:
    DND_FILES = None
    TkinterDnD = None
    HAS_TKINTERDND = False
try:
    import playsound
    HAS_PLAYSOUND = True
except Exception:
    playsound = None
    HAS_PLAYSOUND = False
import logging

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
            if HAS_TKINTERDND and TkinterDnD:
                self.root = TkinterDnD.Tk()
                enable_dnd = True
            else:
                self.root = tk.Tk()
                enable_dnd = False
        else:
            self.root = tk.Toplevel(parent)
            enable_dnd = False

        self.root.title("Outsider v2.00")
        self.root.geometry("1000x700")
        self.root.configure(bg="#111")
        self.root.bind("<Control-w>", lambda e: self.root.destroy())

        self.image_frame = tk.Frame(self.root, bg="#111", bd=2)
        self.image_frame.pack(expand=True, fill="both", padx=8, pady=8)

        # Use a Canvas to support panning & zooming
        self.canvas = tk.Canvas(self.image_frame, bg="#111", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Button-3>", self.show_metadata)
        if enable_dnd and HAS_TKINTERDND:
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind("<<Drop>>", self.on_drop)

        self.build_toolbar()

        self.image_paths = []
        self.current_index = 0
        self.original_image = None
        self.zoom_factor = 1.0
        self.rotation_angle = 0
        self.fullscreen = False
        self.slideshow_running = False

        # Panning state
        self._pan_start = None
        self.offset_x = 0
        self.offset_y = 0

        # Undo history (stores dicts with image and view state)
        self.history = []
        self.history_index = -1

        # Bind canvas events
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.do_pan)
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, "_pan_start", None))
        self.canvas.bind("<Configure>", lambda e: self.display_image())
        # Mouse wheel / scroll (Windows and Linux)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)

        # Keyboard shortcuts
        self.root.bind("<Left>", lambda e: self.show_previous())
        self.root.bind("<Right>", lambda e: self.show_next())
        self.root.bind("+", lambda e: self.zoom_by(1.1, center=None))
        self.root.bind("-", lambda e: self.zoom_by(1/1.1, center=None))
        self.root.bind("<space>", lambda e: self.toggle_slideshow())
        self.root.bind("<Escape>", lambda e: self.toggle_fullscreen() if self.fullscreen else None)
        self.root.bind("r", lambda e: self.rotate_right())
        self.root.bind("R", lambda e: self.rotate_left())
        self.root.bind("u", lambda e: self.undo())
        self.root.bind("<Control-y>", lambda e: self.redo())

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
        add_button("💾 Save As", self.save_as)

        # Editing tools
        add_button("↔ Flip H", self.flip_horizontal)
        add_button("↕ Flip V", self.flip_vertical)
        add_button("🌑 Grayscale", self.apply_grayscale)
        add_button("☀+", lambda: self.adjust_brightness(1.2))
        add_button("☀-", lambda: self.adjust_brightness(0.8))
        add_button("🎚+", lambda: self.adjust_contrast(1.2))
        add_button("🎚-", lambda: self.adjust_contrast(0.8))
        add_button("🎨 Sepia", self.apply_sepia_filter)

        tip = tk.Label(self.root, text="Right-click for metadata | Ctrl+W to close | Space to toggle slideshow | Arrows to navigate | Mouse wheel to zoom | Drag to pan", bg="#111", fg="#555", font=("Arial", 9))
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
            if HAS_PLAYSOUND and playsound:
                threading.Thread(target=playsound.playsound, args=("assets/sounds/error.wav",), daemon=True).start()

    def load_image(self, path):
        try:
            img = Image.open(path)
            img = ImageOps.exif_transpose(img).convert("RGB")
            self.original_image = img
            self.zoom_factor = 1.0
            self.rotation_angle = 0
            self.offset_x = 0
            self.offset_y = 0
            self.push_history()
            self.display_image()
        except Exception as e:
            logging.exception("Failed to load image %s", path)
            messagebox.showerror("Error", f"Failed to load image:\n{e}")

    def display_image(self):
        if self.original_image:
            w, h = self.original_image.size
            new_w = max(1, int(w * self.zoom_factor))
            new_h = max(1, int(h * self.zoom_factor))
            resized = self.original_image.resize((new_w, new_h), Image.LANCZOS)
            rotated = resized.rotate(self.rotation_angle, expand=True)
            self.tk_image = ImageTk.PhotoImage(rotated)
            self.canvas.delete("IMG")
            cx = max(1, self.canvas.winfo_width() // 2)
            cy = max(1, self.canvas.winfo_height() // 2)
            self.canvas.create_image(cx + int(self.offset_x), cy + int(self.offset_y), image=self.tk_image, anchor="center", tags="IMG")
            self.canvas.image = self.tk_image

    def show_previous(self):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.load_image(self.image_paths[self.current_index])

    def show_next(self):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.load_image(self.image_paths[self.current_index])

    def zoom_in(self):
        self.zoom_by(1.25)
        self.push_history()

    def zoom_out(self):
        self.zoom_by(1/1.25)
        self.push_history()

    def rotate_right(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.push_history()
        self.display_image()

    def rotate_left(self):
        self.rotation_angle = (self.rotation_angle - 90) % 360
        self.push_history()
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
            self.push_history()
            self.display_image()

    def flip_vertical(self):
        if self.original_image:
            self.original_image = self.original_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.push_history()
            self.display_image()

    def apply_grayscale(self):
        if self.original_image:
            self.original_image = ImageOps.grayscale(self.original_image).convert("RGB")
            self.push_history()
            self.display_image()

    def adjust_brightness(self, factor):
        if self.original_image:
            enhancer = ImageEnhance.Brightness(self.original_image)
            self.original_image = enhancer.enhance(factor)
            self.push_history()
            self.display_image()

    def adjust_contrast(self, factor):
        if self.original_image:
            enhancer = ImageEnhance.Contrast(self.original_image)
            self.original_image = enhancer.enhance(factor)
            self.push_history()
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
            self.push_history()
            self.display_image()

    def zoom_by(self, factor, center=None):
        # Zoom keeping a point (center) stable if provided; otherwise use canvas center
        try:
            cx = center[0] if center else self.canvas.winfo_width() // 2
            cy = center[1] if center else self.canvas.winfo_height() // 2
        except Exception:
            cx = self.canvas.winfo_width() // 2
            cy = self.canvas.winfo_height() // 2
        old_zoom = self.zoom_factor
        new_zoom = max(0.1, min(10, old_zoom * factor))
        s = new_zoom / old_zoom
        # keep mouse point stable: new_offset = s*old_offset + (1-s)*(mx - cx)
        mx, my = cx, cy
        if center:
            mx, my = center
        self.offset_x = s * self.offset_x + (1 - s) * (mx - (self.canvas.winfo_width() // 2))
        self.offset_y = s * self.offset_y + (1 - s) * (my - (self.canvas.winfo_height() // 2))
        self.zoom_factor = new_zoom
        self.display_image()

    def start_pan(self, event):
        self._pan_start = (event.x, event.y)

    def do_pan(self, event):
        if self._pan_start:
            dx = event.x - self._pan_start[0]
            dy = event.y - self._pan_start[1]
            self.offset_x += dx
            self.offset_y += dy
            self._pan_start = (event.x, event.y)
            self.display_image()

    def on_mouse_wheel(self, event):
        # Windows reports event.delta in multiples of 120, Linux uses Button-4/5
        steps = 0
        if hasattr(event, 'delta'):
            try:
                steps = int(event.delta / 120)
            except Exception:
                steps = 0
        else:
            # Button-4 = scroll up, Button-5 = scroll down
            steps = 1 if getattr(event, 'num', 0) == 4 else -1
        if steps == 0:
            return
        s = 1.1 ** steps
        # zoom centered at mouse cursor
        try:
            cx = self.canvas.winfo_width() // 2
            cy = self.canvas.winfo_height() // 2
            mx, my = event.x, event.y
            old_zoom = self.zoom_factor
            new_zoom = max(0.1, min(10, old_zoom * s))
            scale = new_zoom / old_zoom
            self.offset_x = scale * self.offset_x + (1 - scale) * (mx - cx)
            self.offset_y = scale * self.offset_y + (1 - scale) * (my - cy)
            self.zoom_factor = new_zoom
            self.display_image()
        except Exception:
            logging.exception("Mouse wheel zoom failed")

    def save_as(self):
        if not self.original_image:
            return
        file = filedialog.asksaveasfilename(defaultextension='.jpg', filetypes=[('JPEG', '*.jpg'), ('PNG', '*.png'), ('GIF', '*.gif')], parent=self.root)
        if file:
            try:
                self.original_image.save(file)
                messagebox.showinfo('Saved', f'Saved to {file}')
            except Exception as e:
                logging.exception('Save failed')
                messagebox.showerror('Save Error', str(e))

    def push_history(self):
        if self.original_image is None:
            return
        state = {
            'image': self.original_image.copy(),
            'rotation': self.rotation_angle,
            'zoom': self.zoom_factor,
            'offset_x': self.offset_x,
            'offset_y': self.offset_y,
        }
        # drop any redo history
        self.history = self.history[:self.history_index + 1]
        self.history.append(state)
        if len(self.history) > 20:
            self.history.pop(0)
        self.history_index = len(self.history) - 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.original_image = state['image'].copy()
            self.rotation_angle = state.get('rotation', 0)
            self.zoom_factor = state.get('zoom', 1.0)
            self.offset_x = state.get('offset_x', 0)
            self.offset_y = state.get('offset_y', 0)
            self.display_image()

    def redo(self):
        if self.history_index + 1 < len(self.history):
            self.history_index += 1
            state = self.history[self.history_index]
            self.original_image = state['image'].copy()
            self.rotation_angle = state.get('rotation', 0)
            self.zoom_factor = state.get('zoom', 1.0)
            self.offset_x = state.get('offset_x', 0)
            self.offset_y = state.get('offset_y', 0)
            self.display_image()

    def on_drop(self, event):
        file_path = event.data.strip()
        if os.path.isfile(file_path):
            self.load_image_group(file_path)

def launch():
    Outsider()
