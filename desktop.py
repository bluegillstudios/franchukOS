# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
from Graphics.taskbar import Taskbar, WindowManager
from Graphics.utils import set_background_image, set_background_color
from Applications.file_explorer import FileExplorer
from Applications.terminal import Terminal
from Applications.settings import SettingsApp
from Applications.clock import ClockApp
from Applications.insider import Insider
from Applications.outsider import Outsider
from Applications.franny import FrannyBrowser
from Applications.franpaint import Franpaint
from Applications.games.snake import snake_game as SnakeGame
from Applications.games.spi import SpaceInvaders
from Applications.games.aloha import AlohaGameGUI as Aloha
import threading
import time
from config.manager import load_config
from core.thememanage import apply_theme
import random
import itertools
import os

class Desktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Desktop")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.window_manager = WindowManager(self)
        self.taskbar = Taskbar(self)

        self.icons = []
        self.icon_images = [] 
        self.wallpaper_label = None
        self.current_wallpaper = None
        self.current_theme = None
        self.config = load_config()
        if not isinstance(self.config, dict):
            self.config = {}

        # Dynamic wallpaper attributes
        self.wallpaper_frames = None
        self.wallpaper_index = 0
        self.wallpaper_animating = False

        self.set_wallpaper(self.config.get("wallpaper", "Assets/backgrounds/wallpaper.jpg"))
        apply_theme(self, self.config.get("theme", "light"))
        self.poll_wallpaper_config()
        self.setup_ui()

        # Screensaver
        self.screensaver_timeout = int(self.config.get("screensaver_timeout", 300))
        self.screensaver_active = False
        self.last_activity = time.time()
        self.screensaver_window = None
        self.bind_all("<Any-KeyPress>", self.reset_screensaver_timer)
        self.bind_all("<Any-Button>", self.reset_screensaver_timer)
        self.bind_all("<Motion>", self.reset_screensaver_timer)
        self.start_screensaver_timer()

        # Panic 
        self.start_kernel_panic()
 
    def poll_wallpaper_config(self):
        def watcher():
            while True:
                try:
                    config = load_config()
                    if not isinstance(config, dict):
                        config = {}
                    wallpaper = config.get("wallpaper", "Assets/backgrounds/wallpaper.jpg")
                    if wallpaper != self.current_wallpaper:
                        self.set_wallpaper(wallpaper)
                    theme = config.get("theme", "light")
                    if theme != self.current_theme:
                        self.current_theme = theme
                        apply_theme(self, theme)
                    time.sleep(2)
                except Exception as e:
                    print(f"Wallpaper/theme watcher error: {e}")
                    time.sleep(2)
        threading.Thread(target=watcher, daemon=True).start()

    def set_wallpaper(self, path):
        """Supports static images, animated GIFs, and folder slideshows."""
        try:
            self.current_wallpaper = path
            self.wallpaper_frames = None
            self.wallpaper_animating = False

            if os.path.isdir(path):
                images = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith((".jpg", ".png"))]
                if not images:
                    raise FileNotFoundError("No valid images in slideshow folder")
                self.wallpaper_frames = itertools.cycle(images)
                self.animate_slideshow()
                return

            img = Image.open(path)
            if getattr(img, "is_animated", False):  
                self.wallpaper_frames = [ImageTk.PhotoImage(frame.resize(
                    (self.winfo_screenwidth(), self.winfo_screenheight()), Image.LANCZOS)) 
                    for frame in ImageSequence.Iterator(img)]
                self.wallpaper_index = 0
                self.wallpaper_animating = True
                if not self.wallpaper_label:
                    self.wallpaper_label = tk.Label(self, bd=0)
                    self.wallpaper_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.animate_wallpaper()
                return

            img = img.resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.LANCZOS)
            self.wallpaper_photo = ImageTk.PhotoImage(img)
            if self.wallpaper_label:
                self.wallpaper_label.config(image=self.wallpaper_photo)
            else:
                self.wallpaper_label = tk.Label(self, image=self.wallpaper_photo, bd=0)
                self.wallpaper_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.wallpaper_label.lower()
        except Exception as e:
            print(f"Could not load wallpaper from {path}: {e}")
            self.configure(bg="black")

    def animate_wallpaper(self):
        if not self.wallpaper_animating or not self.wallpaper_frames:
            return
        frame = self.wallpaper_frames[self.wallpaper_index]
        self.wallpaper_label.config(image=frame)
        self.wallpaper_index = (self.wallpaper_index + 1) % len(self.wallpaper_frames)
        self.after(100, self.animate_wallpaper)  

    def animate_slideshow(self):
        if not self.wallpaper_frames:
            return
        path = next(self.wallpaper_frames)
        try:
            img = Image.open(path).resize((self.winfo_screenwidth(), self.winfo_screenheight()), Image.LANCZOS)
            self.wallpaper_photo = ImageTk.PhotoImage(img)
            if self.wallpaper_label:
                self.wallpaper_label.config(image=self.wallpaper_photo)
            else:
                self.wallpaper_label = tk.Label(self, image=self.wallpaper_photo, bd=0)
                self.wallpaper_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.wallpaper_label.lower()
        except Exception as e:
            print(f"Slideshow error: {e}")
        self.after(8000, self.animate_slideshow)  

    def setup_ui(self):
        self.icon_container = tk.Frame(self, bg="", bd=0)
        self.icon_container.place(relx=0, rely=0)
        apps = [
            ("Terminal", "assets/icons/apps/terminal.png", Terminal),
            ("File Explorer", "assets/icons/apps/files.png", FileExplorer),
            ("Settings", "assets/icons/apps/settings.png", SettingsApp),
            ("Clock", "assets/icons/apps/clock.png", ClockApp),
            ("Insider", "assets/icons/apps/insider.png", Insider),
            ("Outsider", "assets/icons/apps/viewer.png", Outsider),
            ("Franny", "assets/icons/apps/franny.png", FrannyBrowser),
            ("Snake", "assets/icons/games/snake.jpg", SnakeGame),
            ("Space Invaders", "assets/icons/games/spi.jpg", SpaceInvaders),
            ("Aloha", "assets/icons/games/aloha.jpg", Aloha),
            ("Franpaint", "assets/icons/apps/franpaint.png", Franpaint),
        ]

        for idx, (name, icon_path, app_class) in enumerate(apps):
            self.create_icon(name, icon_path, app_class, row=idx//5, col=idx%5)

        self.taskbar.lift()
        self.taskbar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_icon(self, name, icon_path, app_class, row, col):
        try:
            icon_img = Image.open(icon_path).resize((64, 64), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon_img)
        except Exception as e:
            print(f"Failed to load icon '{name}' from {icon_path}: {e}")
            return

        icon_frame = tk.Frame(self.icon_container, bg="#000000", bd=0)
        icon_frame.place(x=40 + col * 100, y=40 + row * 100)

        icon_button = tk.Button(
            icon_frame,
            image=icon_photo,
            command=lambda: self.window_manager.launch(app_class),
            bd=0,
            bg="#000000",
            activebackground="#222222"
        )
        icon_button.pack()

        label = tk.Label(icon_frame, text=name, fg="white", bg="#000000", font=("Arial", 10))
        label.pack()

        self.icons.append(icon_frame)
        self.icon_images.append(icon_photo)  

    def reset_screensaver_timer(self, event=None):
        self.last_activity = time.time()
        if self.screensaver_active:
            self.deactivate_screensaver()

    def start_screensaver_timer(self):
        def check():
            while True:
                if not self.screensaver_active and (time.time() - self.last_activity > self.screensaver_timeout):
                    self.activate_screensaver()
                time.sleep(2)
        threading.Thread(target=check, daemon=True).start()

    def activate_screensaver(self):
        self.screensaver_active = True
        self.screensaver_window = tk.Toplevel(self)
        self.screensaver_window.attributes("-fullscreen", True)
        self.screensaver_window.configure(bg="black")
        self.screensaver_window.lift()
        self.screensaver_window.focus_set()
        self.screensaver_window.bind("<Any-KeyPress>", self.reset_screensaver_timer)
        self.screensaver_window.bind("<Any-Button>", self.reset_screensaver_timer)
        self.screensaver_window.bind("<Motion>", self.reset_screensaver_timer)

        try:
            gif = Image.open("Assets/screensavers/fractal.gif")
            frames = [ImageTk.PhotoImage(frame.copy().resize(
                (self.winfo_screenwidth(), self.winfo_screenheight()), Image.LANCZOS)) 
                for frame in ImageSequence.Iterator(gif)]
            label = tk.Label(self.screensaver_window, bd=0)
            label.pack(fill="both", expand=True)

            def animate(index=0):
                if not self.screensaver_active: return
                label.config(image=frames[index])
                self.screensaver_window.after(100, animate, (index + 1) % len(frames))

            animate()
        except Exception as e:
            print(f"Screensaver GIF error: {e}")
            tk.Label(self.screensaver_window, text="Franchuk is waiting. Don't leave him alone.",
                     fg="white", bg="black", font=("Segoe UI", 48)).pack(expand=True)
            
    def deactivate_screensaver(self, event=None):
        if self.screensaver_window:
            self.screensaver_window.destroy()
            self.screensaver_window = None
        self.screensaver_active = False
        self.last_activity = time.time()

    def start_kernel_panic(self):
        def panic_thread():
            while True:
                if random.randint(1, 10000) == 1 and not hasattr(self, "panic_active"):
                    self.after(0, self.show_kernel_panic_screen)
                time.sleep(1)
        threading.Thread(target=panic_thread, daemon=True).start()

    def hex(self, length):
        return "0x" + "".join(random.choice("0123456789ABCDEF") for _ in range(length))

    def registers(self):
        return {
            "dtrace1": self.hex(16),
            "dtrace2": self.hex(16),
            "backtrace1": self.hex(16),
            "backtrace2": self.hex(16),
            "backtrace3": self.hex(16),
            "backtrace4": self.hex(16),
            "dtrace3": self.hex(16),
            "FLAGS": self.hex(8),
            "CRASH_ADDR": self.hex(12)
        }

    def panic_reason(self):
        return random.choice([
            "PAGE_FAULT_IN_NONPAGED_AREA",
            "INVALID_KERNEL_EXECUTION",
            "STACK_BUFFER_OVERRUN",
            "GENERAL_PROTECTION_FAULT",
            "NULL_POINTER_DEREFERENCE",
            "SCHEDULER_CORRUPTION"
        ])

    def show_kernel_panic_screen(self):
        self.panic_active = True

        regs = self.registers()
        reason = self.panic_reason()

        panic = tk.Toplevel(self)
        panic.attributes("-fullscreen", True)
        panic.attributes("-topmost", True)
        panic.overrideredirect(True)
        panic.configure(bg="#050505")

        panic.grab_set()
        panic.focus_force()

        container = tk.Frame(panic, bg="#050505")
        container.pack(expand=True, fill="both", padx=60, pady=40)

        # ASCII mascot
        ascii_mascot = r"""
                    :;ittt+;                .;=tXRRBBBBBRVt;  
                ;tRBMMMMMMMMBV;           ;tBMMMMMBBMMMMMMMMt 
             ;YBMMMBRXYXVRBMMMMBIVBBMBBBBMMMMBRI=iRBMMBRiRMMB 
          ;IBMMBX=:        YBMMMMMMMBBBMMMB+. .iBMMBX;   ;MMV 
        .RMMMB;             ;BMMMBi:   tMM: ;XBMBI;      .MMt 
       ;BMMMM+               RMMM;      BMYBBRi:         ;MM= 
      iBiRMMB                BMMR      +BMMV             iMM: 
     VY  :BMM:              ;MMM=     VMMMMB             RMB  
   :BR    YMMY             .BMMB    ;BMBI;BMX           RMMi  
  =BB:    .BMB:           :BMMB;    BMMt  ;BMR.       ;BMMB   
 iMMR      tMMB.         ;BMB+.    +MMR    ;BMBY: :;IBMMMB.   
:BMM;       RBMB;     :tBMMB;      BMR      ;BMMMMMMMMMR;     
YMMR          ;iRBRRBBMMBV;        ;;         ;iXRRRI;.       
VMB.              ;tYt;:                                      
:R:
"""
        tk.Label(container, text=ascii_mascot, fg="#ff5555", bg="#050505",
                 font=("Consolas", 12), justify="left").pack(anchor="w", pady=(0, 20))

        tk.Label(container, text="Uh oh. Kernel panic.", fg="#ff5555", bg="#050505",
                 font=("Consolas", 42, "bold")).pack(anchor="w")

        tk.Label(container, text=f"STOP CODE: {reason}", fg="white", bg="#050505",
                 font=("Consolas", 18)).pack(anchor="w", pady=(0, 25))

        tk.Label(container, text="CPU REGISTERS:", fg="#aaaaaa", bg="#050505",
                 font=("Consolas", 16, "bold")).pack(anchor="w")

        reg_dump = "\n".join(f"{k:<12} {v}" for k, v in regs.items())
        tk.Label(container, text=reg_dump, fg="#dddddd", bg="#050505",
                 font=("Consolas", 14), justify="left").pack(anchor="w", pady=(0, 30))

        qr_frame = tk.Frame(container, bg="#050505")
        qr_frame.pack(anchor="w")

        try:
            qr_img = Image.open("Assets/panic/qr.png").resize((180, 180), Image.LANCZOS)
            qr_photo = ImageTk.PhotoImage(qr_img)
            qr = tk.Label(qr_frame, image=qr_photo, bg="#050505")
            qr.image = qr_photo
            qr.pack(side="left")
        except Exception as e:
            print(f"QR error: {e}")

        tk.Label(qr_frame,
                 text=(
                     "The system has been halted due to an unsafe process. The operating system needs to be restarted.\n\n"
                     "A crash dump has been written.\n\n"
                     "Scan the QR code for support\n"
                     "or visit: franchukos.local/panic\n\n"
                     f"Uptime: {random.randint(120, 10000)} seconds"
                 ),
                 fg="#cccccc", bg="#050505", font=("Consolas", 14), justify="left").pack(side="left", padx=30)

        progress = tk.Label(container, text="Collecting diagnostic data… 0%", fg="#888888",
                            bg="#050505", font=("Consolas", 14))
        progress.pack(anchor="w", pady=(30, 0))

        def animate(p=0):
            if not self.panic_active:
                return
            if p <= 100:
                progress.config(text=f"Collecting diagnostic data… {p}%")
                panic.after(random.randint(80, 200), animate, p + random.randint(1, 5))

        animate()
        panic.bind("<Control-Alt-r>", lambda e: self._clear_kernel_panic(panic))

    def _clear_kernel_panic(self, panic_window):
        try:
            panic_window.grab_release()
            panic_window.destroy()
        except:
            pass
        if hasattr(self, "panic_active"):
            del self.panic_active


if __name__ == "__main__":
    desktop = Desktop()
    desktop.mainloop()