import tkinter as tk
from tkinter import filedialog
import pygame
from time import time, sleep
import threading
import json
import itertools

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
swing_amount = 0.0  # 0.0 = straight, 0.5 = max swing

key_bindings = {
    "a": "C", "s": "D", "d": "E", "f": "F",
    "g": "G", "h": "A", "j": "B",
    "q": "Kick", "w": "Snare", "e": "HiHat"
}

# --- Undo/Redo stacks ---
undo_stack = []
redo_stack = []

def push_undo():
    undo_stack.append(json.dumps(grid))
    if len(undo_stack) > 50:
        undo_stack.pop(0)

def undo():
    if undo_stack:
        redo_stack.append(json.dumps(grid))
        prev = undo_stack.pop()
        loaded_grid = json.loads(prev)
        for r in range(len(rows)):
            for c in range(steps):
                grid[r][c] = loaded_grid[r][c]
                update_button_color(r, c)

def redo():
    if redo_stack:
        push_undo()
        next_grid = json.loads(redo_stack.pop())
        for r in range(len(rows)):
            for c in range(steps):
                grid[r][c] = next_grid[r][c]
                update_button_color(r, c)

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
    push_undo()
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
        # Swing: delay every other step
        if step % 2 == 0:
            sleep(step_time * (1 + swing_amount))
        else:
            sleep(step_time * (1 - swing_amount))
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

def update_tempo(val):
    global tempo_multiplier
    tempo_multiplier = float(val)

def update_swing(val):
    global swing_amount
    swing_amount = float(val)

def update_master_vol(val):
    global master_volume
    master_volume = float(val)

root = tk.Tk()
root.title(f"{APP_NAME} v{VERSION}")
root.configure(bg="#222")

title_label = tk.Label(root, text=f"{APP_NAME} v{VERSION}", font=("Arial", 20, "bold"), fg="#fff", bg="#222")
title_label.pack(pady=10)

tempo_frame = tk.Frame(root, bg="#222")
tempo_frame.pack(pady=5)
tk.Label(tempo_frame, text="Tempo", font=("Arial", 12), fg="#fff", bg="#222").pack(side=tk.LEFT)
tempo_slider = tk.Scale(tempo_frame, from_=0.5, to=2.0, resolution=0.1, orient=tk.HORIZONTAL,
                        command=update_tempo, bg="#333", fg="#fff", troughcolor="#555", width=15)
tempo_slider.set(1.0)
tempo_slider.pack(side=tk.LEFT, padx=10)

swing_frame = tk.Frame(root, bg="#222")
swing_frame.pack(pady=5)
tk.Label(swing_frame, text="Swing", font=("Arial", 12), fg="#fff", bg="#222").pack(side=tk.LEFT)
swing_slider = tk.Scale(swing_frame, from_=0.0, to=0.5, resolution=0.01, orient=tk.HORIZONTAL,
                        command=update_swing, bg="#333", fg="#fff", troughcolor="#555", width=15)
swing_slider.set(0.0)
swing_slider.pack(side=tk.LEFT, padx=10)

button_frame = tk.Frame(root, bg="#222")
button_frame.pack(pady=10)
buttons = []

for r, row_name in enumerate(rows):
    row_frame = tk.Frame(button_frame, bg="#222")
    row_frame.pack(pady=2)
    tk.Label(row_frame, text=row_name, width=6, font=("Arial", 11, "bold"), fg="#fff", bg="#222").pack(side=tk.LEFT)
    row_buttons = []
    for c in range(steps):
        btn = tk.Button(row_frame, bg="#444", activebackground="#0f0", width=4, height=2,
                        font=("Arial", 10, "bold"),
                        command=lambda r=r, c=c: toggle_cell(r, c))
        btn.pack(side=tk.LEFT, padx=1)
        row_buttons.append(btn)
    buttons.append(row_buttons)

control_frame = tk.Frame(root, bg="#222")
control_frame.pack(pady=10)

loop_var = tk.BooleanVar()
tk.Checkbutton(control_frame, text="Loop", variable=loop_var, command=start_loop,
               font=("Arial", 11), fg="#fff", bg="#222", selectcolor="#333").pack(side=tk.LEFT, padx=5)

tk.Button(control_frame, text="Play Once", command=lambda: threading.Thread(target=play_sequence).start(),
          bg="#4caf50", fg="#fff", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="Save Pattern", command=save_pattern,
          bg="#2196f3", fg="#fff", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="Load Pattern", command=load_pattern,
          bg="#ff9800", fg="#fff", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)

tk.Button(control_frame, text="Undo", command=undo,
          bg="#9e9e9e", fg="#222", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
tk.Button(control_frame, text="Redo", command=redo,
          bg="#9e9e9e", fg="#222", font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)

tk.Label(control_frame, text="Master Vol", font=("Arial", 11), fg="#fff", bg="#222").pack(side=tk.LEFT, padx=5)
master_slider = tk.Scale(control_frame, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL,
                         command=update_master_vol, bg="#333", fg="#fff", troughcolor="#555", width=15)
master_slider.set(1.0)
master_slider.pack(side=tk.LEFT, padx=5)

def key_press(event):
    key = event.char.lower()
    if key in key_bindings:
        play_note(key_bindings[key])
root.bind("<KeyPress>", key_press)

root.mainloop()