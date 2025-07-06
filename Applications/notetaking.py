import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import markdown

APP_NAME = "Notetaking"
NOTES_DIR = "notes"
os.makedirs(NOTES_DIR, exist_ok=True)

class NotetakingApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.filename = None

        # Sidebar
        self.sidebar = tk.Frame(root, width=200, bg="#f0f0f0")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.note_listbox = tk.Listbox(self.sidebar)
        self.note_listbox.pack(fill=tk.BOTH, expand=1, padx=5, pady=5)
        self.note_listbox.bind("<<ListboxSelect>>", self.load_selected_note)

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
            self.root.destroy()

    def confirm_unsaved(self):
        if self.text.edit_modified():
            result = messagebox.askyesnocancel("Unsaved Changes", "Save changes before closing?")
            if result:  # Yes
                self.save_note()
                return True
            elif result is None:  # Cancel
                return False
            else:  # No
                return True
        return True

    def refresh_note_list(self):
        self.note_listbox.delete(0, tk.END)
        for file in sorted(os.listdir(NOTES_DIR)):
            if file.endswith(".txt"):
                self.note_listbox.insert(tk.END, file)

    def load_selected_note(self, event):
        if not self.confirm_unsaved():
            return
        index = self.note_listbox.curselection()
        if index:
            filename = self.note_listbox.get(index[0])
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

def main():
    root = tk.Tk()
    root.geometry("900x600")
    app = NotetakingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()