import tkinter as tk
from tkinter import messagebox, scrolledtext
import random

# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

class AlohaGameGUI:
    def __init__(self, master):
        self.window = tk.Toplevel(master)
        self.window.title("Aloha - Survive the Island")
        self.window.geometry("600x400")
        self.window.resizable(False, False)

        self.island_explored = False
        self.found_food = False
        self.has_boat = False
        self.has_tools = False
        self.wild_animals_encountered = False

        self.text = scrolledtext.ScrolledText(self.window, height=12, width=70, state='disabled', wrap='word', font=("Courier New", 10))
        self.text.pack(padx=10, pady=(10, 5), fill='both', expand=True)

        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(pady=5)

        self.start()

    def clear_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

    def show_text(self, msg):
        self.text.config(state='normal')
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, msg)
        self.text.config(state='disabled')

    def start(self):
        self.show_text("You're stranded on a mysterious island somewhere near Hawaii...")
        self.window.after(1500, self.first_choice)

    def first_choice(self):
        msg = (
            "\nYou wake up on a sandy beach. The sun is shining, and the waves are calm.\n"
            "To the north, there's a dense jungle. To the south, the open ocean.\n"
            "You need to survive. What will you do first?"
        )
        self.show_text(msg)
        self.clear_buttons()
        tk.Button(self.button_frame, text="Explore the jungle", width=30, command=self.explore_jungle).pack(pady=2)
        tk.Button(self.button_frame, text="Walk along the beach", width=30, command=self.walk_beach).pack(pady=2)
        tk.Button(self.button_frame, text="Try to build a boat", width=30, command=self.build_boat).pack(pady=2)

    def explore_jungle(self):
        self.island_explored = True
        self.clear_buttons()
        event = random.choice(['berries', 'tools', 'animal'])
        if event == 'berries':
            self.found_food = True
            msg = (
                "\nYou explore the thick jungle and find bushes with wild berries and a stream of fresh water.\n"
                "You eat and feel refreshed."
            )
        elif event == 'tools':
            self.has_tools = True
            msg = (
                "\nWhile exploring, you find the remains of an old campsite with a rusty knife and some rope.\n"
                "These tools might help later."
            )
        elif event == 'animal':
            self.wild_animals_encountered = True
            msg = (
                "\nA wild boar charges at you in the jungle! You barely escape with a scratch.\n"
                "It’s dangerous out there."
            )
        self.show_text(msg)
        self.window.after(1500, self.next_step)

    def walk_beach(self):
        msg = (
            "\nYou walk along the shore and find footprints — maybe someone else was here?\n"
            "You also find some driftwood that might help you build a raft."
        )
        self.has_tools = True
        self.show_text(msg)
        self.window.after(1500, self.next_step)

    def build_boat(self):
        if not self.has_tools:
            msg = (
                "\nYou try to build a boat with your bare hands, but it's too difficult.\n"
                "You need tools or better materials."
            )
        else:
            self.has_boat = True
            msg = (
                "\nUsing rope, wood, and makeshift tools, you manage to build a small raft.\n"
                "It's not perfect, but it might float."
            )
        self.show_text(msg)
        self.window.after(1500, self.next_step)

    def next_step(self):
        self.clear_buttons()
        if self.island_explored and self.found_food:
            msg = "\nYou've gathered supplies and explored the island. What next?"
            self.show_text(msg)
            if self.has_boat:
                tk.Button(self.button_frame, text="Escape by boat", width=30, command=self.escape_by_boat).pack(pady=2)
            else:
                tk.Button(self.button_frame, text="Escape by boat (need raft)", width=30, state='disabled').pack(pady=2)
            tk.Button(self.button_frame, text="Wait for rescue", width=30, command=self.wait_for_rescue).pack(pady=2)
            tk.Button(self.button_frame, text="Explore again", width=30, command=self.explore_jungle).pack(pady=2)
        else:
            msg = "\nYou're not ready to escape yet. You need more food and supplies."
            self.show_text(msg)
            self.window.after(1500, self.first_choice)

    def escape_by_boat(self):
        self.clear_buttons()
        outcome = random.choice(['success', 'storm', 'lost'])
        if outcome == 'success':
            msg = (
                "\nYou set sail. The sea is rough, but your raft holds together.\n"
                "After days of drifting, a cargo ship spots you!\n"
                "You're saved! Congratulations!"
            )
        elif outcome == 'storm':
            msg = (
                "\nYou sail away, but a storm hits on the second night.\n"
                "The raft breaks apart and you wash back on shore, barely alive.\n"
                "You’ll need a better plan."
            )
            self.has_boat = False
            self.window.after(3000, self.first_choice)
        elif outcome == 'lost':
            msg = (
                "\nYou float away but quickly realize you’ve lost your sense of direction.\n"
                "With no food left, you return to the island exhausted."
            )
            self.has_boat = False
            self.window.after(3000, self.first_choice)

        self.show_text(msg)
        if outcome == 'success':
            self.show_end_options()

    def wait_for_rescue(self):
        self.clear_buttons()
        chance = random.randint(1, 1000)
        if chance == 1:
            msg = (
                "\nYou wait... and wait... Finally, a helicopter flies overhead.\n"
                "You're rescued! You survived!"
            )
            self.show_text(msg)
            self.show_end_options()
        else:
            msg = (
                "\nYou wait for days with no sign of help. Food starts running low.\n"
                "You'll need to find another way out."
            )
            self.show_text(msg)
            self.window.after(3000, self.first_choice)

    def show_end_options(self):
        self.clear_buttons()
        tk.Button(self.button_frame, text="Play Again", width=20, command=self.reset_game).pack(pady=2)
        tk.Button(self.button_frame, text="Quit", width=20, command=self.window.destroy).pack(pady=2)

    def reset_game(self):
        self.island_explored = False
        self.found_food = False
        self.has_boat = False
        self.has_tools = False
        self.wild_animals_encountered = False
        self.start()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main root window
    AlohaGameGUI(root)
    root.mainloop()
