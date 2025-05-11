# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk

def apply_theme(root, theme):
    """
    Apply the given theme to the entire root window and its children.
    """
    if theme == "light":
        root.configure(bg="white")
        for child in root.winfo_children():
            try:
                child.configure(bg="white", fg="black")
            except:
                pass
    elif theme == "dark":
        root.configure(bg="#222222")
        for child in root.winfo_children():
            try:
                child.configure(bg="#222222", fg="white")
            except:
                pass
    else:
        print("Unknown theme:", theme)
