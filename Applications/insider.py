# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from pygame import mixer
import os
import time

class Insider:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Insider v1.12")
        self.root.geometry("700x400")
        self.root.configure(bg="#1e1e1e")

        mixer.init()
        self.playlist = []
        self.current_index = -1
        self.is_playing = False
        self.total_duration = 0

        self.setup_ui()

    def setup_ui(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TButton", background="#333", foreground="white", font=("Segoe UI", 10), padding=5)
        style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 10))
        style.configure("TScale", background="#1e1e1e")

        # Left frame (playlist)
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.playlist_box = tk.Listbox(self.left_frame, bg="#2c2c2c", fg="white", selectbackground="#444", width=30)
        self.playlist_box.pack(fill="y", expand=True)
        self.playlist_box.bind("<Double-1>", self.play_selected)

        self.add_btn = ttk.Button(self.left_frame, text="Add File", command=self.add_to_playlist)
        self.add_btn.pack(pady=5)

        self.remove_btn = ttk.Button(self.left_frame, text="Remove", command=self.remove_from_playlist)
        self.remove_btn.pack(pady=5)

        # Right frame (controls + album art)
        self.right_frame = ttk.Frame(self.root)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.album_art_label = ttk.Label(self.right_frame)
        self.album_art_label.pack(pady=5)

        self.file_label = ttk.Label(self.right_frame, text="No file selected")
        self.file_label.pack(pady=5)

        self.controls_frame = ttk.Frame(self.right_frame)
        self.controls_frame.pack(pady=10)

        self.prev_btn = ttk.Button(self.controls_frame, text="⏮", command=self.prev_track)
        self.prev_btn.grid(row=0, column=0, padx=5)

        self.play_pause_btn = ttk.Button(self.controls_frame, text="▶️", command=self.toggle_play)
        self.play_pause_btn.grid(row=0, column=1, padx=5)

        self.stop_btn = ttk.Button(self.controls_frame, text="⏹", command=self.stop_media)
        self.stop_btn.grid(row=0, column=2, padx=5)

        self.next_btn = ttk.Button(self.controls_frame, text="⏭", command=self.next_track)
        self.next_btn.grid(row=0, column=3, padx=5)

        self.volume_label = ttk.Label(self.right_frame, text="Volume")
        self.volume_label.pack()
        self.volume_scale = ttk.Scale(self.right_frame, from_=0, to=100, orient="horizontal", command=self.adjust_volume)
        self.volume_scale.set(50)
        self.volume_scale.pack(pady=5, fill="x", padx=30)

        self.progress_scale = ttk.Scale(self.right_frame, from_=0, to=100, orient="horizontal", command=self.seek_media)
        self.progress_scale.pack(fill="x", padx=20)

        self.time_label = ttk.Label(self.right_frame, text="00:00 / 00:00")
        self.time_label.pack()

        self.default_album_art()

    def default_album_art(self):
        default = Image.new("RGB", (150, 150), color="#444")
        self.album_image = ImageTk.PhotoImage(default)
        self.album_art_label.config(image=self.album_image)
        self.album_art_label.image = self.album_image  

    def add_to_playlist(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac")])
        for file in files:
            self.playlist.append(file)
            self.playlist_box.insert(tk.END, os.path.basename(file))

    def play_selected(self, event):
        selected = self.playlist_box.curselection()
        if selected:
            self.current_index = selected[0]
            self.play_current()

    def play_current(self):
        if 0 <= self.current_index < len(self.playlist):
            filepath = self.playlist[self.current_index]
            mixer.music.load(filepath)
            mixer.music.play()
            self.total_duration = mixer.Sound(filepath).get_length()
            self.file_label.config(text=os.path.basename(filepath))
            self.update_album_art(filepath)
            self.play_pause_btn.config(text="⏸")
            self.is_playing = True
            self.update_progress()

    def toggle_play(self):
        if self.is_playing:
            mixer.music.pause()
            self.play_pause_btn.config(text="▶️")
            self.is_playing = False
        else:
            if self.current_index == -1 and self.playlist:
                self.current_index = 0
                self.play_current()
            else:
                mixer.music.unpause()
                self.play_pause_btn.config(text="⏸")
                self.is_playing = True

    def stop_media(self):
        mixer.music.stop()
        self.play_pause_btn.config(text="▶️")
        self.is_playing = False

    def next_track(self):
        if self.current_index + 1 < len(self.playlist):
            self.current_index += 1
            self.play_current()

    def prev_track(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.play_current()

    def remove_from_playlist(self):
        selected = self.playlist_box.curselection()
        if selected:
            index = selected[0]
            del self.playlist[index]
            self.playlist_box.delete(index)
            if self.current_index == index:
                self.stop_media()
                self.file_label.config(text="No file selected")
                self.default_album_art()
                self.current_index = -1

    def adjust_volume(self, val):
        mixer.music.set_volume(float(val) / 100)

    def update_progress(self):
        if self.is_playing and 0 <= self.current_index < len(self.playlist):
            pos = mixer.music.get_pos() / 1000
            percent = (pos / self.total_duration) * 100 if self.total_duration else 0
            self.progress_scale.set(percent)

            current_time = time.strftime('%M:%S', time.gmtime(pos))
            total_time = time.strftime('%M:%S', time.gmtime(self.total_duration))
            self.time_label.config(text=f"{current_time} / {total_time}")

            self.root.after(1000, self.update_progress)

    def seek_media(self, val):
        if self.total_duration and self.current_index != -1:
            new_time = (float(val) / 100) * self.total_duration
            mixer.music.play(start=new_time)
            self.play_pause_btn.config(text="⏸")
            self.is_playing = True

    def update_album_art(self, filepath):
        folder = os.path.dirname(filepath)
        cover_path = os.path.join(folder, "cover.jpg")
        if os.path.exists(cover_path):
            img = Image.open(cover_path).resize((150, 150))
        else:
            img = Image.new("RGB", (150, 150), "#444")
        self.album_image = ImageTk.PhotoImage(img)
        self.album_art_label.config(image=self.album_image)
        self.album_art_label.image = self.album_image 

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    player = Insider()
    player.run()