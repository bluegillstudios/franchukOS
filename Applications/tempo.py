import tkinter as tk
from tkinter import filedialog
import pygame
from time import time, sleep
import threading
import json

# why did i do it like this
APP_NAME = "Tempo"
VERSION = "1.0.0"


pygame.mixer.init()

notes = {
    "C": "Applications/sounds/C.aiff",
    "D": "Applications/sounds/D.aiff",
    "E": "Applications/sounds/E.aiff",
    "F": "Applications/sounds/F.aiff",
    "G": "Applications/sounds/G.aiff",
    "A": "Applications/sounds/A.aiff",
    "B": "Applications/sounds/B.aiff",
}

drums = {
    "Kick": "Applications/sounds/kick.wav",
    "Snare": "Applications/sounds/snare.wav",
    "HiHat": "Applications/sounds/hihat.wav"
}

all_sounds = {**notes, **drums}
rows = list(all_sounds.keys())
steps = 16


grid = [[0 for _ in range(steps)] for _ in range(len(rows))]
sequence = []  # live recording
note_volumes = {note: 1.0 for note in notes}
master_volume = 1.0
tempo_multiplier = 1.0

key_bindings = {
    "a": "C", "s": "D", "d": "E", "f": "F",
    "g": "G", "h": "A", "j": "B",
    "q": "Kick", "w": "Snare", "e": "HiHat"
}

def play_sound(file, volume=1.0):
    sound = pygame.mixer.Sound(file)
    sound.set_volume(volume * master_volume)
    sound.play()

def play_note(note):
    if note in notes:
        play_sound(notes[note], volume=note_volumes.get(note, 1.0))
    elif note in drums:
        play_sound(drums[note])
    # Record live note with timestamp
    sequence.append((note, time()))

def toggle_cell(r, c):
    grid[r][c] = 0 if grid[r][c] else 1
    update_button_color(r, c)

def update_button_color(r, c):
    btn = buttons[r][c]
    btn.config(bg="green" if grid[r][c] else "lightgrey")

def highlight_step(step):
    for r in range(len(rows)):
        buttons[r][step].config(relief=tk.SUNKEN)

def unhighlight_step(step):
    for r in range(len(rows)):
        buttons[r][step].config(relief=tk.RAISED)

def play_sequence():
    step_time = 0.5 / tempo_multiplier
    for step in range(steps):
        highlight_step(step)
        for r, row in enumerate(grid):
            if row[step]:
                play_sound(all_sounds[rows[r]])
        sleep(step_time)
        unhighlight_step(step)

def start_loop():
    def loop():
        while loop_var.get():
            play_sequence()
    threading.Thread(target=loop, daemon=True).start()

def save_pattern():
    file_path = filedialog.asksaveasfilename(defaultextension=".json")
    if file_path:
        with open(file_path, "w") as f:
            json.dump(grid, f)
        print(f"Pattern saved to {file_path}")

def load_pattern():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, "r") as f:
            loaded_grid = json.load(f)
        for r in range(len(rows)):
            for c in range(steps):
                grid[r][c] = loaded_grid[r][c]
                update_button_color(r, c)
        print(f"Pattern loaded from {file_path}")

root = tk.Tk()
root.title(f"{APP_NAME} v{VERSION}")

def update_tempo(val):
    global tempo_multiplier
    tempo_multiplier = float(val)
tempo_slider = tk.Scale(root, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                        label="Tempo", command=update_tempo)
tempo_slider.set(1.0)
tempo_slider.pack()
button_frame = tk.Frame(root)
button_frame.pack()
buttons = []

for r, row_name in enumerate(rows):
    row_frame = tk.Frame(button_frame)
    row_frame.pack()
    tk.Label(row_frame, text=row_name, width=6).pack(side=tk.LEFT)
    row_buttons = []
    for c in range(steps):
        btn = tk.Button(row_frame, bg="lightgrey", width=3, height=1,
                        command=lambda r=r, c=c: toggle_cell(r, c))
        btn.pack(side=tk.LEFT)
        row_buttons.append(btn)
    buttons.append(row_buttons)
control_frame = tk.Frame(root)
control_frame.pack()

loop_var = tk.BooleanVar()
tk.Checkbutton(control_frame, text="Loop", variable=loop_var, command=start_loop).pack(side=tk.LEFT)

tk.Button(control_frame, text="Play Once", command=lambda: threading.Thread(target=play_sequence).start(), bg="lightgreen").pack(side=tk.LEFT)
tk.Button(control_frame, text="Save Pattern", command=save_pattern, bg="lightblue").pack(side=tk.LEFT)
tk.Button(control_frame, text="Load Pattern", command=load_pattern, bg="orange").pack(side=tk.LEFT)

def update_master_vol(val):
    global master_volume
    master_volume = float(val)
tk.Label(control_frame, text="Master Vol").pack(side=tk.LEFT)

master_slider = tk.Scale(control_frame, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, command=update_master_vol)
master_slider.set(1.0)
master_slider.pack(side=tk.LEFT)

def key_press(event):
    key = event.char.lower()
    if key in key_bindings:
        play_note(key_bindings[key])
root.bind("<KeyPress>", key_press)

root.mainloop()