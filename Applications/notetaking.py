import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import markdown

APP_NAME = "Notetaking"
NOTES_DIR = "notes"
PINS_FILE = "pins.json"
os.makedirs(NOTES_DIR, exist_ok=True)

# Load or create pin data
if os.path.exists(PINS_FILE):
    with open(PINS_FILE, "r") as f:
        pinned_notes = json.load(f)
else:
    pinned_notes = []

class NotetakingApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.filename = None
        self.dark_mode = False

        # Sidebar
        self.sidebar = tk.Frame(root, width=200, bg="#f0f0f0")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.note_listbox = tk.Listbox(self.sidebar)
        self.note_listbox.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)
        self.note_listbox.bind("<<ListboxSelect>>", self.load_selected_note)
        self.note_listbox.bind("<Button-3>", self.right_click_note)

        self.refresh_note_list()

        # Text Area
        self.text = tk.Text(root, undo=True, font=("Arial", 12))
        self.text.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.text.edit_modified(False)

        # Menu Bar
        menubar = tk.Menu(root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_note)
        file_menu.add_command(label="Open...", command=self.open_note)
        file_menu.add_command(label="Save", command=self.save_note)
        file_menu.add_command(label="Save As...", command=self.save_note_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Preview Markdown", command=self.preview_markdown)
        view_menu.add_command(label="Toggle Dark Mode", command=self.toggle_dark_mode)
        menubar.add_cascade(label="View", menu=view_menu)

        root.config(menu=menubar)

    def new_note(self):
        if self.confirm_unsaved():
            self.text.delete(1.0, tk.END)
            self.filename = None
            self.root.title(f"{APP_NAME} - New Note")

    def open_note(self):
        if not self.confirm_unsaved():
            return
        path = filedialog.askopenfilename(initialdir=NOTES_DIR, defaultextension=".txt",
                                          filetypes=[("Text files", "*.txt")])
        if path:
            self.load_note(path)

    def save_note(self):
        if not self.filename:
            return self.save_note_as()
        with open(self.filename, "w", encoding="utf-8") as file:
            file.write(self.text.get(1.0, tk.END).rstrip())
        self.text.edit_modified(False)
        self.refresh_note_list()
        messagebox.showinfo("Saved", "Note saved successfully!")

    def save_note_as(self):
        path = filedialog.asksaveasfilename(initialdir=NOTES_DIR, defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt")])
        if path:
            self.filename = path
            self.save_note()

    def exit_app(self):
        if self.confirm_unsaved():
            self.save_pins()
            self.root.destroy()

    def confirm_unsaved(self):
        if self.text.edit_modified():
            result = messagebox.askyesnocancel("Unsaved Changes", "Save changes before closing?")
            if result:
                self.save_note()
                return True
            elif result is None:
                return False
            else:
                return True
        return True

    def refresh_note_list(self):
        self.note_listbox.delete(0, tk.END)
        notes = sorted([f for f in os.listdir(NOTES_DIR) if f.endswith(".txt")])
        pinned = [n for n in pinned_notes if n in notes]
        unpinned = [n for n in notes if n not in pinned]
        for note in pinned + unpinned:
            label = f"📌 {note}" if note in pinned else note
            self.note_listbox.insert(tk.END, label)

    def load_selected_note(self, event):
        if not self.confirm_unsaved():
            return
        index = self.note_listbox.curselection()
        if index:
            label = self.note_listbox.get(index[0])
            filename = label.replace("📌 ", "")
            path = os.path.join(NOTES_DIR, filename)
            self.load_note(path)

    def load_note(self, path):
        with open(path, "r", encoding="utf-8") as file:
            self.text.delete(1.0, tk.END)
            self.text.insert(tk.END, file.read())
        self.filename = path
        self.text.edit_modified(False)
        self.root.title(f"{APP_NAME} - {os.path.basename(path)}")

    def preview_markdown(self):
        html = markdown.markdown(self.text.get(1.0, tk.END))
        preview_win = tk.Toplevel(self.root)
        preview_win.title("Markdown Preview")
        preview_win.geometry("600x500")

        preview_text = scrolledtext.ScrolledText(preview_win, wrap=tk.WORD, font=("Arial", 11))
        preview_text.pack(fill=tk.BOTH, expand=1)
        preview_text.insert(tk.END, html)
        preview_text.config(state=tk.DISABLED)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg = "#1e1e1e" if self.dark_mode else "white"
        fg = "#dcdcdc" if self.dark_mode else "black"
        sb_bg = "#2e2e2e" if self.dark_mode else "#f0f0f0"

        self.text.config(bg=bg, fg=fg, insertbackground=fg)
        self.sidebar.config(bg=sb_bg)
        self.note_listbox.config(bg=bg, fg=fg, selectbackground="#444")

    def right_click_note(self, event):
        index = self.note_listbox.nearest(event.y)
        self.note_listbox.selection_clear(0, tk.END)
        self.note_listbox.selection_set(index)
        label = self.note_listbox.get(index)
        filename = label.replace("📌 ", "")

        menu = tk.Menu(self.root, tearoff=0)
        if filename in pinned_notes:
            menu.add_command(label="Unpin", command=lambda: self.unpin_note(filename))
        else:
            menu.add_command(label="Pin", command=lambda: self.pin_note(filename))
        menu.post(event.x_root, event.y_root)

    def pin_note(self, filename):
        if filename not in pinned_notes:
            pinned_notes.append(filename)
        self.save_pins()
        self.refresh_note_list()

    def unpin_note(self, filename):
        if filename in pinned_notes:
            pinned_notes.remove(filename)
        self.save_pins()
        self.refresh_note_list()

    def save_pins(self):
        with open(PINS_FILE, "w") as f:
            json.dump(pinned_notes, f)

def main():
    root = tk.Tk()
    root.geometry("900x600")
    app = NotetakingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()