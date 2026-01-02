# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
import threading
from Graphics.login import LoginApp  
from desktop import Desktop
from Graphics.taskbar import Taskbar
import pygame
from PIL import Image, ImageTk, ImageOps, ImageDraw
import time
from colorama import init, Fore
import os

init()
print(Fore.RED + 'BM: STABLE BUILD, M37. REV182')
time.sleep(0.25)
print(Fore.RESET + '[    2.8351] I/QTTranslations: Loaded translation file for language EN.')
time.sleep(0.05)
print("[    2.8451] I/QTTranslations: Loaded translation file for language FR.")
time.sleep(0.05)
print("[    2.8451] I/QTTranslations: Loaded translation file for language ES.")
time.sleep(0.05)
print("[    8.4575] V/Bus: RAM is mapped at 0x149f65e0000.")
time.sleep(0.05)

print("[  427.9675] V/Bus: BIOS is mapped at 0x149f2280000.")
time.sleep(0.05)

print("[  427.9676] V/Bus: LUTs are mapped at 0x149f88b0000.")
time.sleep(0.05)

print("[  427.9976] I/Bus: Fastmem base: 00000149FE8B0000")
time.sleep(0.05)

print("[  428.2207] I/Host: Trying to create a D3D11 GPU device...")
time.sleep(0.05)

print("[  429.3501] I/GPUDevice: Render window is 800x500.")
time.sleep(0.05)

print("[  429.5671] I/GPUDevice: Graphics Driver Info:")
time.sleep(0.05)

print("[  429.5675] D3D_FEATURE_LEVEL_11_0 (sm50)")
time.sleep(0.05)

print("[  429.5765] I/GPU_HW: Resolution Scale: 1 (800x500), maximum 16")
time.sleep(0.05)

print("[  429.5767] I/GPU_HW: Multisampling: 1x")
time.sleep(0.05)

print("[  429.5768] I/GPU_HW: Dithering: Disabled")
time.sleep(0.05)

print("[  429.5768] I/GPU_HW: Texture Filtering: Nearest-Neighbor")
time.sleep(0.05)

print("[  429.5769] I/GPU_HW: Dual-source blending: Supported")
time.sleep(0.05)
print("[  429.5770] I/GPU_HW: Clamping UVs: NO")
time.sleep(0.05)
print("[  429.5770] I/GPU_HW: Depth buffer: NO")
time.sleep(0.05)

print("[  429.5771] I/GPU_HW: Downsampling: Disabled")
time.sleep(0.05)

print("[  429.5772] I/GPU_HW: Wireframe rendering: Disabled")
time.sleep(0.05)
print(Fore.GREEN + 'Process all done! :)')
time.sleep(0.10)

def show_loading_files():
    """Display flickering file listing from key directories"""
    directories = ["Graphics", "assets", "Desktop", "Applications", "service", "crypto", "core"]
    files_to_show = []
    
    for directory in directories:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                if os.path.isfile(os.path.join(directory, file)):
                    files_to_show.append(f"{directory}/{file}")
    
    for file in files_to_show:
        print(Fore.BLUE + 'Loading files: %s' % file)
        time.sleep(0.1)

show_loading_files()
print(Fore.GREEN + 'Process all done! :)')
time.sleep(0.10)
print(Fore.RESET + 'Please wait....')
time.sleep(3)

SPLASH_DURATION = 7  # seconds

def show_splash(next_step_callback):
    class SplashScreen(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Loading...")
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            self.geometry(f"{screen_width}x{screen_height}+0+0")
            self.overrideredirect(True)
            self.configure(bg="white")

            # Load images
            logo_img = Image.open("assets/icons/logo.png")
            logo_img = ImageOps.contain(logo_img, (128, 128), Image.LANCZOS)

            text_img = Image.open("assets/icons/holdon.png")
            text_img = ImageOps.contain(text_img, (300, 64), Image.LANCZOS)

            self.logo_photo = ImageTk.PhotoImage(logo_img)
            self.text_photo = ImageTk.PhotoImage(text_img)

            # Place logo
            logo_label = tk.Label(self, image=self.logo_photo, bd=0, bg="white")
            logo_label.place(relx=0.5, rely=0.35, anchor="center")

            # Place text
            text_label = tk.Label(self, image=self.text_photo, bd=0, bg="white")
            text_label.place(relx=0.5, rely=0.7, anchor="center")

            # Create loading bubble frames
            self.loading_frames = []
            self.loading_frame_count = 12
            size = 48
            for i in range(self.loading_frame_count):
                img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
                draw = ImageDraw.Draw(img)
                angle = i * (360 // self.loading_frame_count)
                draw.arc([6, 6, size-6, size-6], angle, angle+270, fill=(0, 120, 255), width=6)
                self.loading_frames.append(ImageTk.PhotoImage(img))

            self.loading_label = tk.Label(self, bg="white")
            self.loading_label.place(relx=0.5, rely=0.55, anchor="center")
            self.loading_index = 0
            self.animate_loading()

        def animate_loading(self):
            self.loading_label.config(image=self.loading_frames[self.loading_index])
            self.loading_index = (self.loading_index + 1) % self.loading_frame_count
            self.after(80, self.animate_loading)

    splash = SplashScreen()

    # Play startup sound in a thread
    def play_startup_sound():
        pygame.mixer.init()
        pygame.mixer.music.load("assets/sounds/startup.wav")
        pygame.mixer.music.play()
    threading.Thread(
        target=play_startup_sound,
        daemon=True
    ).start()

    def close_splash():
        splash.destroy()
        next_step_callback()

    splash.after(SPLASH_DURATION * 1000, close_splash)
    splash.mainloop()

def start_login():
    login = LoginApp()
    login.run()  # Wait for login to complete
    desktop = Desktop()
    taskbar = Taskbar()
    threading.Thread(target=desktop.run, daemon=True).start()
    threading.Thread(target=taskbar.run, daemon=True).start()
    
def main():
    show_splash(start_login)

if __name__ == "__main__":
    main()
