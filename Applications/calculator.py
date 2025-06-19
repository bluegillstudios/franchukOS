import tkinter as tk

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("300x400")
        self.configure(bg="#1e1e1e")
        self.resizable(False, False)

        self.expression = ""

        self.display_frame = self.create_display_frame()
        self.buttons_frame = self.create_buttons_frame()

        self.total_label, self.current_label = self.create_display_labels()
        self.create_buttons()

    def create_display_frame(self):
        frame = tk.Frame(self, height=100, bg="#1e1e1e")
        frame.pack(expand=True, fill="both")
        return frame

    def create_display_labels(self):
        total_label = tk.Label(self.display_frame, text="", anchor=tk.E, bg="#1e1e1e", fg="#888", padx=24, font=("Consolas", 16))
        total_label.pack(expand=True, fill="both")

        current_label = tk.Label(self.display_frame, text="", anchor=tk.E, bg="#1e1e1e", fg="#fff", padx=24, font=("Consolas", 28))
        current_label.pack(expand=True, fill="both")

        return total_label, current_label

    def create_buttons_frame(self):
        frame = tk.Frame(self, bg="#2e2e2e")
        frame.pack(expand=True, fill="both")
        return frame

    def create_buttons(self):
        buttons = [
            ["C", "⌫", "/", "*"],
            ["7", "8", "9", "-"],
            ["4", "5", "6", "+"],
            ["1", "2", "3", "="],
            ["0", ".", "", ""]
        ]

        for row in range(len(buttons)):
            self.buttons_frame.rowconfigure(row, weight=1)
            for col in range(4):
                self.buttons_frame.columnconfigure(col, weight=1)
                if buttons[row][col] != "":
                    self.create_button(buttons[row][col], row, col)

    def create_button(self, text, row, col):
        button = tk.Button(
            self.buttons_frame, text=text, font=("Consolas", 20), border=0,
            bg="#3b3b3b", fg="#ffffff", activebackground="#505050", activeforeground="#00ffcc",
            command=lambda: self.button_action(text)
        )
        button.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

    def button_action(self, key):
        if key == "C":
            self.expression = ""
        elif key == "⌫":
            self.expression = self.expression[:-1]
        elif key == "=":
            try:
                result = str(eval(self.expression))
                self.expression = result
            except Exception:
                self.expression = "Error"
        else:
            self.expression += key
        self.update_display()

    def update_display(self):
        self.total_label.config(text="")
        self.current_label.config(text=self.expression)

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()