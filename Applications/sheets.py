# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import messagebox
import re

class SimpleSheet(tk.Tk):
    def __init__(self, rows=25000, cols=5):
        super().__init__()
        self.title("Sheets")
        self.rows = rows
        self.cols = cols
        self.cells = {}
        self.data = {}
        self.evaluating = set()

        self.create_menu()
        self.create_widgets()

    def create_menu(self):
        menubar = tk.Menu(self)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Guide", command=self.show_guide)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.config(menu=menubar)

    def show_guide(self):
        guide = (
            "Sheets Guide:\n"
            "- Enter numbers or formulas (start with '=') in cells.\n"
            "- Use formulas like '=A1+B2' or '=SUM(A1:A10)'.\n"
            "- Click 'Clear All' to reset the sheet.\n"
            "- Use scrollbars to navigate large sheets.\n"
            "- Circular references show as 'CIRC'.\n"
            "- Only visible cells are loaded for performance."
        )
        messagebox.showinfo("Sheets Guide", guide)

    def create_widgets(self):
        # Scrollable frame setup
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(container)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        v_scroll = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll = tk.Scrollbar(container, orient="horizontal", command=self.canvas.xview)
        h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.sheet_frame = tk.Frame(self.canvas)
        self.sheet_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.sheet_frame, anchor="nw")

        # Column headers
        for c in range(self.cols):
            label = tk.Label(self.sheet_frame, text=chr(ord('A') + c), borderwidth=1, relief="solid", width=10)
            label.grid(row=0, column=c+1, sticky="nsew")

        # Row headers and visible cells (show only first 100 rows for performance)
        self.visible_rows = 100
        for r in range(self.visible_rows):
            label = tk.Label(self.sheet_frame, text=str(r+1), borderwidth=1, relief="solid", width=4)
            label.grid(row=r+1, column=0, sticky="nsew")
            for c in range(self.cols):
                entry = tk.Entry(self.sheet_frame, width=10)
                entry.grid(row=r+1, column=c+1, sticky="nsew")
                entry.bind("<FocusOut>", self.on_focus_out)
                entry.bind("<FocusIn>", self.on_focus_in)
                self.cells[(r, c)] = entry

        # Clear button
        clear_btn = tk.Button(self, text="Clear All", command=self.clear_all)
        clear_btn.grid(row=1, column=0, columnspan=self.cols+1, sticky="we")

        # Bind scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self.top_row = 0
        self.update_cells()

    def _on_mousewheel(self, event):
        # Scroll vertically and update visible rows
        delta = -1 if event.delta > 0 else 1
        new_top = self.top_row + delta * 5
        self.show_rows(max(0, min(self.rows - self.visible_rows, new_top)))

    def _on_canvas_resize(self, event):
        self.canvas.itemconfig(self.sheet_frame, width=event.width)

    def show_rows(self, top_row):
        self.top_row = top_row
        for r in range(self.visible_rows):
            row_num = top_row + r
            for c in range(self.cols):
                entry = self.cells.get((r, c))
                if entry:
                    val = self.data.get((row_num, c), "")
                    entry.delete(0, tk.END)
                    entry.insert(0, val)
        # Update row headers
        for r in range(self.visible_rows):
            label = self.sheet_frame.grid_slaves(row=r+1, column=0)
            if label:
                label[0].config(text=str(top_row + r + 1))

    def on_focus_out(self, event):
        widget = event.widget
        for (r, c), cell in self.cells.items():
            if cell == widget:
                value = cell.get()
                self.data[(self.top_row + r, c)] = value
                self.update_cells()
                break

    def on_focus_in(self, event):
        widget = event.widget
        for (r, c), cell in self.cells.items():
            if cell == widget:
                raw_val = self.data.get((self.top_row + r, c), "")
                cell.delete(0, tk.END)
                cell.insert(0, raw_val)
                break

    def clear_all(self):
        self.data.clear()
        self.update_cells()

    def update_cells(self):
        for (r, c), cell in self.cells.items():
            row_num = self.top_row + r
            raw_val = self.data.get((row_num, c), "")
            if isinstance(raw_val, str) and raw_val.startswith("="):
                val = self.safe_evaluate_formula(raw_val[1:], row_num, c)
                cell.delete(0, tk.END)
                cell.insert(0, str(val))
            else:
                cell.delete(0, tk.END)
                cell.insert(0, raw_val)

    def safe_evaluate_formula(self, formula, cur_row, cur_col):
        if (cur_row, cur_col) in self.evaluating:
            return "CIRC"  # Circular ref detected
        self.evaluating.add((cur_row, cur_col))
        val = self.evaluate_formula(formula, cur_row, cur_col)
        self.evaluating.remove((cur_row, cur_col))
        return val

    def evaluate_formula(self, formula, cur_row, cur_col):
        # Support SUM function and cell references with ranges
        formula = formula.strip()

        # Handle SUM function, e.g. SUM(A1:A3)
        sum_match = re.match(r'^SUM\(([^)]+)\)$', formula, re.IGNORECASE)
        if sum_match:
            range_str = sum_match.group(1)
            cells = self.parse_range(range_str)
            s = 0.0
            for (r, c) in cells:
                val = self.get_cell_value(r, c)
                try:
                    s += float(val)
                except:
                    pass
            return s

        # Replace cell refs in formula with their values
        cell_ref_re = re.compile(r'\b([A-Z])([1-9][0-9]*)\b')

        def repl(m):
            col = ord(m.group(1)) - ord('A')
            row = int(m.group(2)) - 1
            if 0 <= row < self.rows and 0 <= col < self.cols:
                val = self.get_cell_value(row, col)
                return str(val)
            else:
                return "0"

        expr = cell_ref_re.sub(repl, formula)

        # Allow only safe characters (digits, operators, parentheses, dot, space)
        if not re.match(r'^[0-9+\-*/(). ]*$', expr):
            return "ERR"

        try:
            return eval(expr)
        except:
            return "ERR"

    def parse_range(self, range_str):
        """
        Parses a range like "A1:A3" or "B2:D4"
        Returns list of (row, col) tuples.
        """
        if ':' not in range_str:
            # Single cell
            m = re.match(r'^([A-Z])([1-9][0-9]*)$', range_str.strip())
            if m:
                col = ord(m.group(1)) - ord('A')
                row = int(m.group(2)) - 1
                return [(row, col)]
            else:
                return []

        start_str, end_str = range_str.split(':')
        m1 = re.match(r'^([A-Z])([1-9][0-9]*)$', start_str.strip())
        m2 = re.match(r'^([A-Z])([1-9][0-9]*)$', end_str.strip())
        if not m1 or not m2:
            return []

        start_col = ord(m1.group(1)) - ord('A')
        start_row = int(m1.group(2)) - 1
        end_col = ord(m2.group(1)) - ord('A')
        end_row = int(m2.group(2)) - 1

        rows = range(min(start_row, end_row), max(start_row, end_row)+1)
        cols = range(min(start_col, end_col), max(start_col, end_col)+1)
        cells = [(r, c) for r in rows for c in cols if 0 <= r < self.rows and 0 <= c < self.cols]
        return cells

    def get_cell_value(self, row, col):
        val = self.data.get((row, col), "")
        if isinstance(val, str) and val.startswith("="):
            return self.safe_evaluate_formula(val[1:], row, col)
        else:
            try:
                return float(val)
            except:
                return 0

if __name__ == "__main__":
    app = SimpleSheet()
    app.mainloop()
