# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import filedialog
from pygame import mixer
import os

class Insider:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Insider v1.03")
        self.root.geometry("500x300")
        self.root.configure(bg="black")

        mixer.init()  # Initialize the mixer module for audio

        self.current_file = None

        # Play/Pause button
        self.play_pause_btn = tk.Button(self.root, text="Play", command=self.toggle_play, bg="gray")
        self.play_pause_btn.pack(pady=10)

        # Stop button
        self.stop_btn = tk.Button(self.root, text="Stop", command=self.stop_media, bg="gray")
        self.stop_btn.pack(pady=5)

        # Volume control
        self.volume_label = tk.Label(self.root, text="Volume", bg="black", fg="white")
        self.volume_label.pack()
        self.volume_scale = tk.Scale(self.root, from_=0, to_=100, orient="horizontal", command=self.adjust_volume)
        self.volume_scale.set(50)  # Default volume level
        self.volume_scale.pack(pady=5)

        # Progress Bar (this will be updated during playback)
        self.progress_bar = tk.Scale(self.root, from_=0, to_=100, orient="horizontal", state="disabled")
        self.progress_bar.pack(pady=5)

        # Open File button
        self.open_file_btn = tk.Button(self.root, text="Open File", command=self.open_file, bg="gray")
        self.open_file_btn.pack(pady=10)

        # Play state
        self.is_playing = False

    def toggle_play(self):
        """Toggle play/pause functionality"""
        if self.is_playing:
            mixer.music.pause()
            self.play_pause_btn.config(text="Play")
        else:
            if not self.current_file:
                self.open_file()  # Open a file if no media is loaded
            else:
                mixer.music.unpause()
                self.play_pause_btn.config(text="Pause")
        self.is_playing = not self.is_playing

    def stop_media(self):
        """Stop the media playback"""
        mixer.music.stop()
        self.play_pause_btn.config(text="Play")
        self.is_playing = False

    def adjust_volume(self, val):
        """Adjust the volume of the media"""
        volume = int(val) / 100
        mixer.music.set_volume(volume)

    def open_file(self):
        """Open a file using a file dialog"""
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav *.ogg *.flac")])
        if file_path:
            self.current_file = file_path
            mixer.music.load(file_path)
            mixer.music.play()
            self.play_pause_btn.config(text="Pause")
            self.is_playing = True
            self.update_progress()

    def update_progress(self):
        """Update the progress bar while the media is playing"""
        if self.is_playing:
            current_pos = mixer.music.get_pos() / 1000  # Get position in seconds
            duration = mixer.Sound(self.current_file).get_length()
            progress = (current_pos / duration) * 100
            self.progress_bar.set(progress)
            self.root.after(1000, self.update_progress)

    def run(self):
        """Run the Tkinter main loop"""
        self.root.mainloop()

if __name__ == "__main__":
    player = Insider()
    player.run()
