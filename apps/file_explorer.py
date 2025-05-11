# Copyright 2025 the FranchukOS project authors. 
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import os
import shutil
import subprocess
import platform
from datetime import datetime
from PIL import Image, ImageTk

class FileExplorer(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("File Explorer")
        self.geometry("800x600")
        self.current_dir = os.getcwd()
        self.clipboard = None
        self.clipboard_action = None

        self.path_label = tk.Label(self, text=self.current_dir, bg="black", fg="lime", font=("Courier", 12))
        self.path_label.pack(fill="x", padx=10, pady=5)

        self.search_entry = tk.Entry(self, bg="black", fg="lime", font=("Courier", 10))
        self.search_entry.pack(fill="x", padx=10, pady=5)
        self.search_entry.bind("<KeyRelease>", self.search_files)

        self.listbox = tk.Listbox(self, bg="black", fg="lime", font=("Courier", 10), selectmode=tk.SINGLE)
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.listbox.bind("<Double-1>", self.on_item_double_click)
        self.listbox.bind("<Button-3>", self.show_context_menu)
        self.listbox.bind("<B1-Motion>", self.drag_file)
        self.listbox.bind("<ButtonRelease-1>", self.drop_file)

        self.context_menu = tk.Menu(self, tearoff=0, bg="black", fg="lime")
        self.context_menu.add_command(label="Open", command=self.context_open)
        self.context_menu.add_command(label="Rename", command=self.rename_item)
        self.context_menu.add_command(label="Delete", command=self.delete_item)
        self.context_menu.add_command(label="Copy", command=self.copy_item)
        self.context_menu.add_command(label="Cut", command=self.cut_item)
        self.context_menu.add_command(label="Paste", command=self.paste_item)

        self.populate_directory(self.current_dir)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(fill="x", padx=10, pady=5)

        self.up_button = tk.Button(self.button_frame, text="Up", command=self.go_up, bg="black", fg="lime")
        self.up_button.pack(side="left", padx=5)

        self.refresh_button = tk.Button(self.button_frame, text="Refresh", command=self.refresh, bg="black", fg="lime")
        self.refresh_button.pack(side="left", padx=5)

        self.new_file_button = tk.Button(self.button_frame, text="New File", command=self.create_new_file, bg="black", fg="lime")
        self.new_file_button.pack(side="left", padx=5)

        self.new_folder_button = tk.Button(self.button_frame, text="New Folder", command=self.create_new_folder, bg="black", fg="lime")
        self.new_folder_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_item, bg="black", fg="lime")
        self.delete_button.pack(side="left", padx=5)

        self.rename_button = tk.Button(self.button_frame, text="Rename", command=self.rename_item, bg="black", fg="lime")
        self.rename_button.pack(side="left", padx=5)

    def populate_directory(self, path):
        self.listbox.delete(0, tk.END)
        self.path_label.config(text=path)
        try:
            items = os.listdir(path)
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    display_name = f"[DIR] {item}"
                else:
                    size = os.path.getsize(item_path)
                    modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime("%Y-%m-%d %H:%M")
                    display_name = f"{item} ({size} B, {modified})"
                self.listbox.insert(tk.END, display_name)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def on_item_double_click(self, event):
        selected_item = self.listbox.get(self.listbox.curselection()).strip()
        if "[DIR]" in selected_item:
            selected_item = selected_item[6:]
        else:
            selected_item = selected_item.split(" (")[0]

        item_path = os.path.join(self.current_dir, selected_item)

        if os.path.isdir(item_path):
            self.current_dir = item_path
            self.populate_directory(item_path)
        else:
            self.open_file(selected_item)

    def open_file(self, file_name):
        file_path = os.path.join(self.current_dir, file_name)
        try:
            if file_name.endswith('.txt'):
                with open(file_path, "r") as file:
                    content = file.read()
                    self.show_file_content(file_name, content)
            elif file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                self.show_image_preview(file_name, file_path)
            else:
                self.open_external(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file {file_path}: {str(e)}")

    def open_external(self, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {str(e)}")

    def show_file_content(self, file_name, content):
        file_window = tk.Toplevel(self)
        file_window.title(file_name)
        text_area = tk.Text(file_window, bg="black", fg="lime", font=("Courier", 10))
        text_area.pack(fill="both", expand=True)
        text_area.insert("1.0", content)
        text_area.config(state=tk.DISABLED)

    def show_image_preview(self, file_name, file_path):
        file_window = tk.Toplevel(self)
        file_window.title(f"Preview: {file_name}")
        try:
            img = Image.open(file_path)
            img.thumbnail((400, 400))
            img = ImageTk.PhotoImage(img)
            panel = tk.Label(file_window, image=img)
            panel.image = img
            panel.pack()
        except Exception as e:
            messagebox.showerror("Error", f"Could not display image preview: {str(e)}")

    def go_up(self):
        parent_dir = os.path.dirname(self.current_dir)
        if parent_dir != self.current_dir:
            self.current_dir = parent_dir
            self.populate_directory(self.current_dir)

    def refresh(self):
        self.populate_directory(self.current_dir)

    def create_new_file(self):
        new_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if new_file_path:
            try:
                with open(new_file_path, "w") as file:
                    file.write("")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {str(e)}")

    def create_new_folder(self):
        folder_name = simpledialog.askstring("New Folder", "Enter folder name:")
        if folder_name:
            folder_path = os.path.join(self.current_dir, folder_name)
            try:
                os.makedirs(folder_path)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder: {str(e)}")

    def delete_item(self):
        selected_item = self.listbox.get(self.listbox.curselection()).strip()
        item_name = selected_item[6:] if selected_item.startswith("[DIR] ") else selected_item.split(" (")[0]
        item_path = os.path.join(self.current_dir, item_name)

        if os.path.isdir(item_path):
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the directory '{item_name}'?")
            if confirm:
                try:
                    shutil.rmtree(item_path)
                    self.refresh()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete directory: {str(e)}")
        else:
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the file '{item_name}'?")
            if confirm:
                try:
                    os.remove(item_path)
                    self.refresh()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not delete file: {str(e)}")

    def rename_item(self):
        selected_item = self.listbox.get(self.listbox.curselection()).strip()
        old_name = selected_item[6:] if selected_item.startswith("[DIR] ") else selected_item.split(" (")[0]
        new_name = simpledialog.askstring("Rename", f"Enter a new name for '{old_name}':")

        if new_name:
            old_path = os.path.join(self.current_dir, old_name)
            new_path = os.path.join(self.current_dir, new_name)
            try:
                os.rename(old_path, new_path)
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename {old_name} to {new_name}: {str(e)}")

    def search_files(self, event):
        search_term = self.search_entry.get().lower()
        self.listbox.delete(0, tk.END)

        try:
            items = os.listdir(self.current_dir)
            for item in items:
                if search_term in item.lower():
                    item_path = os.path.join(self.current_dir, item)
                    display_name = f"[DIR] {item}" if os.path.isdir(item_path) else item
                    self.listbox.insert(tk.END, display_name)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_context_menu(self, event):
        try:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.listbox.nearest(event.y))
            self.context_menu.post(event.x_root, event.y_root)
        except:
            pass

    def context_open(self):
        try:
            self.on_item_double_click(None)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open item: {str(e)}")

    def copy_item(self):
        item = self.listbox.get(self.listbox.curselection()).strip()
        self.clipboard = item[6:] if item.startswith("[DIR] ") else item.split(" (")[0]
        self.clipboard_action = "copy"

    def cut_item(self):
        item = self.listbox.get(self.listbox.curselection()).strip()
        self.clipboard = item[6:] if item.startswith("[DIR] ") else item.split(" (")[0]
        self.clipboard_action = "cut"

    def paste_item(self):
        if self.clipboard:
            src_path = os.path.join(self.current_dir, self.clipboard)
            dest_path = os.path.join(self.current_dir, f"Copy of {self.clipboard}")
            try:
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
                if self.clipboard_action == "cut":
                    if os.path.isdir(src_path):
                        shutil.rmtree(src_path)
                    else:
                        os.remove(src_path)
                self.refresh()
                self.clipboard = None
                self.clipboard_action = None
            except Exception as e:
                messagebox.showerror("Error", f"Paste failed: {str(e)}")

    def drag_file(self, event):
        try:
            self.listbox.selection_set(self.listbox.nearest(event.y))
        except:
            pass

    def drop_file(self, event):
        try:
            src_index = self.listbox.curselection()[0]
            src_item = self.listbox.get(src_index).strip()
            src_name = src_item[6:] if src_item.startswith("[DIR] ") else src_item.split(" (")[0]
            src_path = os.path.join(self.current_dir, src_name)

            dest_index = self.listbox.nearest(event.y)
            if dest_index == src_index:
                return  # Dropped on itself, do nothing

            dest_item = self.listbox.get(dest_index).strip()
            if dest_item.startswith("[DIR] "):
                dest_name = dest_item[6:]
                dest_path = os.path.join(self.current_dir, dest_name)
                if not os.path.isdir(dest_path):
                    return
            else:
                # If dropped on a file, move to its parent directory (current)
                dest_path = self.current_dir

            # Prevent moving a folder into itself or its subfolder
            if os.path.isdir(src_path) and os.path.commonpath([src_path]) == os.path.commonpath([src_path, dest_path]):
                messagebox.showerror("Error", "Cannot move a folder into itself or its subfolder.")
                return

            new_path = os.path.join(dest_path, os.path.basename(src_path))
            if os.path.exists(new_path):
                messagebox.showerror("Error", f"Destination already has '{os.path.basename(src_path)}'.")
                return

            shutil.move(src_path, new_path)
            self.refresh()
        except Exception as e:
            # Ignore if no selection or invalid drop
            pass