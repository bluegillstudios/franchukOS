# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import shutil
import platform
import subprocess
from datetime import datetime
from PIL import Image, ImageTk

class FileExplorer(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("File Explorer")
        self.geometry("1000x600")
        self.configure(bg="#101010")
        self.current_dir = os.getcwd()
        self.clipboard = None
        self.clipboard_action = None

        self.setup_ui()
        self.populate_directory(self.current_dir)

    def setup_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, bg="#f0f0f0", height=30)
        toolbar.pack(side="top", fill="x")

        def add_toolbar_button(text, cmd):
            btn = tk.Button(toolbar, text=text, command=cmd, bg="#f0f0f0", relief="flat", font=("Segoe UI", 9))
            btn.pack(side="left", padx=5, pady=2)

        add_toolbar_button("Up", self.go_up)
        add_toolbar_button("Refresh", self.refresh)
        add_toolbar_button("File", self.create_new_file)
        add_toolbar_button("Folder", self.create_new_folder)
        add_toolbar_button("Rename", self.rename_item)
        add_toolbar_button("Delete", self.delete_item)
        add_toolbar_button("Paste", self.paste_item)

        # Path and Search Bar
        path_frame = tk.Frame(self, bg="#ffffff")
        path_frame.pack(fill="x", padx=10, pady=2)

        self.path_label = tk.Label(path_frame, text=self.current_dir, anchor="w", font=("Segoe UI", 10), bg="white")
        self.path_label.pack(side="left", fill="x", expand=True)

        self.search_entry = tk.Entry(path_frame, font=("Segoe UI", 10))
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", self.search_files)

        # File Table View
        self.tree = ttk.Treeview(self, columns=("Name", "Size", "Modified"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Modified", text="Date Modified")
        self.tree.column("Name", anchor="w", width=300)
        self.tree.column("Size", anchor="e", width=100)
        self.tree.column("Modified", anchor="center", width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # Bind double-click
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.context_open)
        self.context_menu.add_command(label="Rename", command=self.rename_item)
        self.context_menu.add_command(label="Delete", command=self.delete_item)
        self.context_menu.add_command(label="Copy", command=self.copy_item)
        self.context_menu.add_command(label="Cut", command=self.cut_item)

    def populate_directory(self, path):
        self.tree.delete(*self.tree.get_children())
        self.path_label.config(text=path)
        try:
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    size = "---"
                else:
                    size = f"{os.path.getsize(item_path)} B"
                modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%Y-%m-%d %H:%M")
                self.tree.insert("", "end", values=(item, size, modified))
        except Exception as e:
            messagebox.showerror("Error", f"Could not list directory: {str(e)}")

    def on_item_double_click(self, event):
        selected = self.get_selected_item()
        if not selected:
            return
        item_path = os.path.join(self.current_dir, selected)
        if os.path.isdir(item_path):
            self.current_dir = item_path
            self.populate_directory(item_path)
        else:
            self.open_file(selected)

    def get_selected_item(self):
        selected = self.tree.focus()
        if selected:
            return self.tree.item(selected, 'values')[0]
        return None

    def open_file(self, name):
        path = os.path.join(self.current_dir, name)
        try:
            if name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                self.show_image_preview(name, path)
            elif name.endswith('.txt'):
                with open(path, "r") as f:
                    content = f.read()
                    self.show_file_content(name, content)
            else:
                self.open_external(path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_external(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open: {str(e)}")

    def show_file_content(self, title, content):
        win = tk.Toplevel(self)
        win.title(title)
        txt = tk.Text(win, bg="black", fg="lime", font=("Courier", 10))
        txt.pack(fill="both", expand=True)
        txt.insert("1.0", content)
        txt.config(state=tk.DISABLED)

    def show_image_preview(self, name, path):
        win = tk.Toplevel(self)
        win.title(f"Preview: {name}")
        try:
            img = Image.open(path)
            img.thumbnail((500, 500))
            img = ImageTk.PhotoImage(img)
            lbl = tk.Label(win, image=img)
            lbl.image = img
            lbl.pack()
        except Exception as e:
            messagebox.showerror("Error", f"Image error: {str(e)}")

    def go_up(self):
        parent = os.path.dirname(self.current_dir)
        if parent != self.current_dir:
            self.current_dir = parent
            self.populate_directory(self.current_dir)

    def refresh(self):
        self.populate_directory(self.current_dir)

    def create_new_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if path:
            try:
                with open(path, "w"): pass
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def create_new_folder(self):
        name = simpledialog.askstring("New Folder", "Folder name:")
        if name:
            try:
                os.makedirs(os.path.join(self.current_dir, name))
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_item(self):
        name = self.get_selected_item()
        if not name:
            return
        path = os.path.join(self.current_dir, name)
        confirm = messagebox.askyesno("Confirm Delete", f"Delete '{name}'?")
        if confirm:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def rename_item(self):
        old_name = self.get_selected_item()
        if not old_name:
            return
        new_name = simpledialog.askstring("Rename", f"Rename '{old_name}' to:")
        if new_name:
            try:
                os.rename(os.path.join(self.current_dir, old_name),
                          os.path.join(self.current_dir, new_name))
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def search_files(self, event):
        term = self.search_entry.get().lower()
        self.listbox.delete(0, tk.END)
        for item in os.listdir(self.current_dir):
            if term in item.lower():
                display_name = f"[DIR] {item}" if os.path.isdir(os.path.join(self.current_dir, item)) else item
                self.listbox.insert(tk.END, display_name)

    def show_context_menu(self, event):
        try:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.listbox.nearest(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        except:
            pass

    def context_open(self):
        self.on_item_double_click(None)

    def copy_item(self):
        item = self.get_selected_item()
        if item:
            self.clipboard = item
            self.clipboard_action = "copy"

    def cut_item(self):
        item = self.get_selected_item()
        if item:
            self.clipboard = item
            self.clipboard_action = "cut"

    def paste_item(self):
        if not self.clipboard:
            return
        src = os.path.join(self.current_dir, self.clipboard)
        dst = os.path.join(self.current_dir, f"Copy of {self.clipboard}")
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            if self.clipboard_action == "cut":
                if os.path.isdir(src):
                    shutil.rmtree(src)
                else:
                    os.remove(src)
            self.refresh()
            self.clipboard = None
        except Exception as e:
            messagebox.showerror("Error", f"Paste failed: {str(e)}")
    def run(self):
        self.mainloop()
        