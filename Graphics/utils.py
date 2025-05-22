# Copyright 2025 the FranchukOS project authors. 
# Contributed under the Apache License, Version 2.0.


import tkinter as tk
from PIL import Image, ImageTk

_background_refs = {}

def set_background_image(widget, image_path):
    image = Image.open(image_path)
    image = image.resize((widget.winfo_width(), widget.winfo_height()), Image.LANCZOS)
    photo = ImageTk.PhotoImage(image)

    bg_label = tk.Label(widget, image=photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    _background_refs[widget] = photo

def set_background_color(widget, color):
    widget.configure(bg=color)
    for child in widget.winfo_children():
        try:
            child.configure(bg=color)
        except:
            pass
