import tkinter as tk
from tkinter import messagebox

# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.


class AlohaGameGUI:
    def __init__(self, root):
        self.root = root
        # self.root.title("Aloha")
        self.island_explored = False
        self.found_food = False
        self.has_boat = False

        self.text = tk.Text(root, height=12, width=60, state='disabled', wrap='word')
        self.text.pack(padx=10, pady=10)

        self.button_frame = tk.Frame(root)
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
        self.show_text("You're stranded on a deserted island near Hawaii.")
        self.root.after(1000, self.first_choice)

    def first_choice(self):
        msg = (
            "\nYou wake up on a sandy beach. The sun is shining, and the waves are calm.\n"
            "You see a dense jungle to the north and the open ocean to the south.\n"
            "Where do you want to go?"
        )
        self.show_text(msg)
        self.clear_buttons()
        tk.Button(self.button_frame, text="Explore the jungle", width=25, command=self.explore_jungle).pack(pady=2)
        tk.Button(self.button_frame, text="Walk along the beach", width=25, command=self.walk_beach).pack(pady=2)
        tk.Button(self.button_frame, text="Try to build a boat", width=25, command=self.build_boat).pack(pady=2)

    def explore_jungle(self):
        msg = (
            "\nYou venture into the jungle, and after some time, you find some wild berries.\n"
            "You eat some and feel a bit better. You also spot a stream of fresh water."
        )
        self.found_food = True
        self.island_explored = True
        self.show_text(msg)
        self.root.after(1000, self.next_step)

    def walk_beach(self):
        msg = (
            "\nYou walk along the beach and see nothing but sand and ocean.\n"
            "After a few hours, you're tired, but at least you've gotten some fresh air."
        )
        self.show_text(msg)
        self.root.after(1000, self.next_step)

    def build_boat(self):
        msg = (
            "\nYou gather materials and attempt to build a boat.\n"
            "It's a lot of hard work, but after several attempts, you've crafted a simple raft."
        )
        self.has_boat = True
        self.show_text(msg)
        self.root.after(1000, self.next_step)

    def next_step(self):
        self.clear_buttons()
        if self.island_explored and self.found_food:
            msg = (
                "\nYou've explored the island and found food. Do you want to try escaping?"
            )
            self.show_text(msg)
            if self.has_boat:
                tk.Button(self.button_frame, text="Try to escape by boat", width=25, command=self.escape_by_boat).pack(pady=2)
            else:
                tk.Button(self.button_frame, text="Try to escape by boat (need a boat!)", width=25, state='disabled').pack(pady=2)
            tk.Button(self.button_frame, text="Stay on the island and wait for rescue", width=35, command=self.wait_for_rescue).pack(pady=2)
        else:
            msg = (
                "\nYou still need to explore more of the island or find food before making any big decisions."
            )
            self.show_text(msg)
            self.root.after(1000, self.first_choice)

    def escape_by_boat(self):
        msg = (
            "\nYou set sail on your raft, battling the waves. After days of struggle, you finally reach a nearby island and are rescued!\n"
            "Congratulations, you escaped the island!"
        )
        self.show_text(msg)
        self.clear_buttons()
        tk.Button(self.button_frame, text="Play Again", width=20, command=self.reset_game).pack(pady=2)
        tk.Button(self.button_frame, text="Quit", width=20, command=self.root.quit).pack(pady=2)

    def wait_for_rescue(self):
        msg = (
            "\nYou decide to stay and wait for rescue. Eventually, a ship finds you and takes you home.\n"
            "Congratulations, you're safe!"
        )
        self.show_text(msg)
        self.clear_buttons()
        tk.Button(self.button_frame, text="Play Again", width=20, command=self.reset_game).pack(pady=2)
        tk.Button(self.button_frame, text="Quit", width=20, command=self.root.quit).pack(pady=2)

    def reset_game(self):
        self.island_explored = False
        self.found_food = False
        self.has_boat = False
        self.start()

if __name__ == "__main__":
    root = tk.Tk()
    game = AlohaGameGUI(root)
    root.mainloop()
