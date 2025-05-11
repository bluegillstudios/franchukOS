# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

class AlohaGame:
    def __init__(self):
        self.island_explored = False
        self.found_food = False
        self.has_boat = False

    def start(self):
        print("You're stranded on a deserted island near Hawaii.")
        self.first_choice()

    def first_choice(self):
        print("\nYou wake up on a sandy beach. The sun is shining, and the waves are calm.")
        print("You see a dense jungle to the north and the open ocean to the south.")
        print("Where do you want to go?")
        print("1. Explore the jungle.")
        print("2. Walk along the beach.")
        print("3. Try to build a boat.")

        choice = input("> ")

        if choice == "1":
            self.explore_jungle()
        elif choice == "2":
            self.walk_beach()
        elif choice == "3":
            self.build_boat()
        else:
            print("Invalid choice. Try again.")
            self.first_choice()

    def explore_jungle(self):
        print("\nYou venture into the jungle, and after some time, you find some wild berries.")
        print("You eat some and feel a bit better. You also spot a stream of fresh water.")
        self.found_food = True
        self.island_explored = True
        self.next_step()

    def walk_beach(self):
        print("\nYou walk along the beach and see nothing but sand and ocean.")
        print("After a few hours, you're tired, but at least you've gotten some fresh air.")
        self.next_step()

    def build_boat(self):
        print("\nYou gather materials and attempt to build a boat.")
        print("It's a lot of hard work, but after several attempts, you've crafted a simple raft.")
        self.has_boat = True
        self.next_step()

    def next_step(self):
        if self.island_explored and self.found_food:
            print("\nYou've explored the island and found food. Do you want to try escaping?")
            print("1. Try to escape by boat.")
            print("2. Stay on the island and wait for rescue.")
            choice = input("> ")

            if choice == "1" and self.has_boat:
                print("\nYou set sail on your raft, battling the waves. After days of struggle, you finally reach a nearby island and are rescued!")
                print("Congratulations, you escaped the island!")
            elif choice == "2":
                print("\nYou decide to stay and wait for rescue. Eventually, a ship finds you and takes you home.")
                print("Congratulations, you're safe!")
            else:
                print("You need a boat to escape!")
                self.first_choice()
        else:
            print("\nYou still need to explore more of the island or find food before making any big decisions.")
            self.first_choice()

if __name__ == "__main__":
    game = AlohaGame()
    game.start()
