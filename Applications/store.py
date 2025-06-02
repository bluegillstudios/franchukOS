# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0. See in the LICENSE file.

import os
import urllib.request
import tarfile
import json
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import requests
from bs4 import BeautifulSoup
import ar
import subprocess
import platform
import shutil

DOWNLOADS_DIR = '../downloads'
BINARES_DIR = '../Binares/installed_apps'
REGISTRY_FILE = '../Binares/registry.json'

# Ensure folders exist
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(BINARES_DIR, exist_ok=True)

# ------------------ Core Functions ------------------

def download_deb(url):
    filename = url.split('/')[-1]
    path = os.path.join(DOWNLOADS_DIR, filename)
    if os.path.exists(path):
        print(f"Using cached {filename}")
        return path
    try:
        urllib.request.urlretrieve(url, path)
        return path
    except Exception as e:
        messagebox.showerror("Download Error", str(e))
        return None

def extract_deb(deb_path, app_name):
    app_path = os.path.join(BINARES_DIR, app_name)
    os.makedirs(app_path, exist_ok=True)
    try:
        with open(deb_path, 'rb') as f:
            archive = ar.Archive(f)
            for entry in archive:
                fname = entry.name.decode() if isinstance(entry.name, bytes) else entry.name
                if fname.startswith('data.tar'):
                    ext = fname.split('.')[-1]
                    temp_tar_path = f'temp_data.tar.{ext}'
                    with open(temp_tar_path, 'wb') as temp_tar:
                        temp_tar.write(entry.data)  

                    with tarfile.open(temp_tar_path, 'r:*') as tar:
                        tar.extractall(app_path)
                    os.remove(temp_tar_path)
                    return app_path
    except Exception as e:
        messagebox.showerror("Extraction Error", str(e))
    return None

def register_app(app_name, app_path):
    registry = load_registry()
    registry[app_name] = app_path
    save_registry(registry)

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE) as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except Exception:
            return {}
    return {}

def save_registry(registry):
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(registry, f, indent=2)

def uninstall_app():
    selected = app_listbox.curselection()
    if not selected:
        return
    app_name = app_listbox.get(selected[0])
    registry = load_registry()
    if app_name in registry:
        app_path = registry[app_name]
        if messagebox.askyesno("Uninstall", f"Are you sure you want to uninstall {app_name}?"):
            try:
                shutil.rmtree(app_path)
                del registry[app_name]
                save_registry(registry)
                refresh_installed_apps()
                messagebox.showinfo("Uninstalled", f"{app_name} removed.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

def run_app():
    selected = app_listbox.curselection()
    if not selected:
        return
    app_name = app_listbox.get(selected[0])
    registry = load_registry()
    app_path = registry.get(app_name)
    if not app_path:
        return

    # Try to find a binary
    bin_dir = os.path.join(app_path, 'usr', 'bin')
    if not os.path.exists(bin_dir):
        messagebox.showwarning("No Executable", f"No binaries found in {bin_dir}")
        return

    for filename in os.listdir(bin_dir):
        full_path = os.path.join(bin_dir, filename)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            try:
                if platform.system() == "Windows":
                    subprocess.Popen(["wsl", full_path])
                else:
                    subprocess.Popen([full_path])
                return
            except Exception as e:
                messagebox.showerror("Run Error", str(e))
                return
    messagebox.showinfo("Not Found", "No runnable binary found.")

# ------------------ Debian Search ------------------

def search_debian_packages(query):
    search_url = f"https://packages.debian.org/stable/search?keywords={query}&searchon=names&suite=stable&section=all"
    try:
        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = soup.select("ul li a[href^='/stable/']")
        return {a.text: f"https://packages.debian.org{a['href']}" for a in results}
    except Exception as e:
        messagebox.showerror("Search Error", str(e))
        return {}

def choose_from_list(title, options):
    selected = [None]

    def on_select():
        try:
            selected[0] = listbox.get(listbox.curselection())
            popup.destroy()
        except:
            pass

    popup = tk.Toplevel()
    popup.title(title)
    popup.geometry("350x300")

    listbox = tk.Listbox(popup, width=50, height=15)
    listbox.pack(padx=10, pady=10, fill=tk.BOTH)
    for opt in options:
        listbox.insert(tk.END, opt)

    tk.Button(popup, text="Select", command=on_select).pack(pady=5)
    popup.wait_window()
    return selected[0]

def get_deb_download_url(package_page_url):
    try:
        response = requests.get(package_page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        arch_links = soup.select("ul li a[href*='architecture']")

        arch_options = {a.text: a['href'] for a in arch_links if any(x in a.text for x in ['amd64', 'i386', 'arm64'])}
        if not arch_options:
            return None

        selected_arch = choose_from_list("Select Architecture", list(arch_options.keys()))
        if not selected_arch:
            return None

        arch_url = f"https://packages.debian.org{arch_options[selected_arch]}"
        arch_page = requests.get(arch_url)
        arch_soup = BeautifulSoup(arch_page.text, 'html.parser')
        deb_link = arch_soup.find('a', href=True, text=lambda x: x and x.endswith('.deb'))
        return deb_link['href'] if deb_link else None
    except Exception as e:
        messagebox.showerror("Download Link Error", str(e))
        return None

def search_and_install_app():
    query = simpledialog.askstring("Search Debian", "Enter app name:")
    if not query:
        return
    packages = search_debian_packages(query)
    if not packages:
        messagebox.showinfo("No Results", "No packages found.")
        return

    selected = choose_from_list("Select App", list(packages.keys()))
    if not selected or selected not in packages:
        return

    app_url = packages[selected]
    deb_url = get_deb_download_url(app_url)
    if not deb_url:
        messagebox.showerror("Error", "Could not find a .deb file.")
        return

    deb_path = download_deb(deb_url)
    if deb_path:
        install_path = extract_deb(deb_path, selected)
        if install_path:
            register_app(selected, install_path)
            messagebox.showinfo("Installed", f"{selected} installed.")
            refresh_installed_apps()

# ------------------ Import/Export ------------------

def export_registry():
    path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if not path:
        return
    registry = load_registry()
    with open(path, 'w') as f:
        json.dump(registry, f, indent=2)
    messagebox.showinfo("Exported", f"Saved to {path}")

def import_registry():
    path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not path:
        return
    try:
        with open(path) as f:
            data = json.load(f)
        save_registry(data)
        messagebox.showinfo("Imported", f"Loaded from {path}")
        refresh_installed_apps()
    except Exception as e:
        messagebox.showerror("Import Error", str(e))

# ------------------ GUI ------------------

def install_from_url():
    url = simpledialog.askstring("Enter URL", "Paste the URL of the .deb package:")
    if not url:
        return
    app_name = simpledialog.askstring("App Name", "Enter a name for the app:")
    if not app_name:
        return
    deb_path = download_deb(url)
    if deb_path:
        install_path = extract_deb(deb_path, app_name)
        if install_path:
            register_app(app_name, install_path)
            messagebox.showinfo("Success", f"{app_name} installed.")
            refresh_installed_apps()

def install_from_file():
    deb_path = filedialog.askopenfilename(title="Select a .deb file", filetypes=[("Debian Package", "*.deb")])
    if not deb_path:
        return
    app_name = simpledialog.askstring("App Name", "Enter a name for the app:")
    if not app_name:
        return
    install_path = extract_deb(deb_path, app_name)
    if install_path:
        register_app(app_name, install_path)
        messagebox.showinfo("Success", f"{app_name} installed.")
        refresh_installed_apps()

def show_app_path():
    selected = app_listbox.curselection()
    if not selected:
        return
    app_name = app_listbox.get(selected[0])
    registry = load_registry()
    path = registry.get(app_name, "Unknown")
    messagebox.showinfo("App Path", f"{app_name} is installed at:\n{path}")

def refresh_installed_apps():
    app_listbox.delete(0, tk.END)
    registry = load_registry()
    for app in registry:
        app_listbox.insert(tk.END, app)

# ------------------ GUI ------------------

def update_status(msg):
    status_var.set(msg)
    root.update_idletasks()

root = tk.Tk()
root.title("Franny's Pop Shop v1.0.441.1 (Unstable)")
root.geometry("800x500")
root.configure(bg="#f0f0f0")

# Fonts and colors
BTN_FONT = ("Segoe UI", 10)
LABEL_FONT = ("Segoe UI", 11, "bold")
LIST_FONT = ("Consolas", 10)
BG_COLOR = "#ffffff"
SIDEBAR_COLOR = "#e0e0e0"

# ----- Sidebar -----
sidebar = tk.Frame(root, bg=SIDEBAR_COLOR, width=200)
sidebar.pack(side="left", fill="y")

def add_sidebar_button(text, command):
    btn = tk.Button(sidebar, text=text, font=BTN_FONT, command=command, bg="white", relief="flat", anchor="w")
    btn.pack(fill="x", padx=10, pady=4)

add_sidebar_button("🔍 Search & Install", search_and_install_app)
add_sidebar_button("🌐 Install from URL", install_from_url)
add_sidebar_button("Install From File", lambda: (
    lambda deb_path=filedialog.askopenfilename(title="Select a .deb file", filetypes=[("Debian Package", "*.deb")]):
        shutil.copy(deb_path, os.path.join(DOWNLOADS_DIR, os.path.basename(deb_path)))
        if deb_path else None
)())
add_sidebar_button("▶️ Run App", run_app)
add_sidebar_button("🗑 Uninstall App", uninstall_app)
add_sidebar_button("📄 Show App Path", show_app_path)
add_sidebar_button("📤 Export List", export_registry)
add_sidebar_button("📥 Import List", import_registry)
add_sidebar_button("🔄 Refresh", lambda: refresh_installed_apps())

# ----- Main Panel -----
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(side="left", fill="both", expand=True)

tk.Label(main_frame, text="Installed Apps", font=LABEL_FONT, bg=BG_COLOR).pack(pady=(10, 0))

app_listbox = tk.Listbox(main_frame, font=LIST_FONT, height=15, selectmode="browse")
app_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# ----- App Info Panel -----
app_info = tk.Label(main_frame, text="Select an app to see details.", anchor="w", justify="left", bg=BG_COLOR, font=("Segoe UI", 9))
app_info.pack(fill="x", padx=10, pady=(0, 10))

# ----- Status Bar -----
status_var = tk.StringVar(value="Welcome to Franny's Pop Shop!")
status_bar = tk.Label(root, textvariable=status_var, relief="sunken", anchor="w", font=("Segoe UI", 9), bg="#dddddd")
status_bar.pack(side="bottom", fill="x")

# ----- App Info Updates -----
def on_app_select(event=None):
    selected = app_listbox.curselection()
    if not selected:
        app_info.config(text="Select an app to see details.")
        return
    app_name = app_listbox.get(selected[0])
    path = load_registry().get(app_name, "Unknown")
    app_info.config(text=f"{app_name}\nPath: {path}")

app_listbox.bind("<<ListboxSelect>>", on_app_select)

# ----- Refresh apps on launch -----
refresh_installed_apps()

# ----- Start the GUI loop -----
root.mainloop()