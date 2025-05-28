# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import tkinter as tk
from tkinter import ttk
import code
import sys
import io
import os
import shutil
import platform
import psutil
import datetime
import time
import getpass

class Terminal(tk.Toplevel):
    PROMPT = ">>> "

    def __init__(self, master=None):
        super().__init__(master)
        self.title("FranchukOS Terminal v0.7")
        self.geometry("800x500")
        self.configure(bg="#1e1e1e")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TText", background="#1e1e1e", foreground="#1a5e1a", font=("Consolas", 11))

        self.text = tk.Text(self, bg="#1e1e1e", fg="#00ff00", insertbackground="white",
                            font=("Consolas", 11), undo=True, wrap="word",
                            borderwidth=0, highlightthickness=0, padx=10, pady=10)
        self.text.pack(fill="both", expand=True, padx=10, pady=10)
        self.text.insert("end", "Welcome to the Terminal, v0.7\n" + self.PROMPT)
        self.text.bind("<Return>", self.handle_enter)
        self.text.bind("<Up>", self.history_up)
        self.text.bind("<Down>", self.history_down)
        self.text.focus_set()

        self.cmd_buffer = ""
        self.cmd_history = []
        self.history_index = -1
        self.interpreter = code.InteractiveInterpreter()

        self.commands = {
            "list": self.list_files,
            "dir": self.list_files,
            "clear": self.clear_terminal,
            "exit": self.quit_terminal,
            "pwd": self.print_working_directory,
            "cd": self.change_directory,
            "mkdir": self.make_directory,
            "rmdir": self.remove_directory,
            "rm": self.remove_file,
            "cp": self.copy_file,
            "mv": self.move_file,
            "cat": self.cat_file,
            "echo": self.echo_text,
            "time": self.show_time,
            "date": self.show_date,
            "df": self.show_disk_space,
            "free": self.show_memory_info,
            "uptime": self.show_uptime,
            "ps": self.show_processes,
            "kill": self.kill_process,
            "whoami": self.show_current_user,
            "hostname": self.show_hostname,
            "ip": self.show_ip_address,
            "arch": self.show_architecture,
            "python": self.run_python_interpreter,
            "help": self.show_help,
            "version": lambda args: "FranchukOS version 30.1.1.6379.132 (codenamed Rainier). Terminal version v0.7.4.2",
            "rename": self.rename_file,
        }

    def handle_enter(self, event=None):
        # Get the current line (from the prompt onwards)
        index = self.text.index("insert linestart")
        line = self.text.get(index, "insert lineend")
        # Only the part after the prompt
        if line.startswith(self.PROMPT):
            code_line = line[len(self.PROMPT):].strip()
        else:
            code_line = line.strip()
        self.text.insert("end", "\n")
        if code_line:
            self.cmd_history.append(code_line)
        self.history_index = len(self.cmd_history)
        output = self.run_code(code_line)
        if output:
            self.text.insert("end", output.strip() + "\n")
        self.text.insert("end", self.PROMPT)
        self.text.see("end")
        return "break"

    def history_up(self, event=None):
        if self.cmd_history and self.history_index > 0:
            self.history_index -= 1
            self.replace_current_line(self.cmd_history[self.history_index])
        return "break"

    def history_down(self, event=None):
        if self.cmd_history and self.history_index < len(self.cmd_history) - 1:
            self.history_index += 1
            self.replace_current_line(self.cmd_history[self.history_index])
        else:
            self.replace_current_line("")
        return "break"

    def replace_current_line(self, text):
        # Delete everything after the prompt on the current line, then insert
        line_start = self.text.index("insert linestart")
        prompt_len = len(self.PROMPT)
        self.text.delete(f"{line_start}+{prompt_len}c", f"{line_start} lineend")
        self.text.insert(f"{line_start}+{prompt_len}c", text)

    def run_code(self, code_line):
        if not code_line:
            return ""
        parts = code_line.split()
        cmd, args = parts[0], parts[1:]

        if cmd in self.commands:
            try:
                result = self.commands[cmd](args)
                return result if result is not None else ""
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            # Fallback: try to execute as python code
            stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            try:
                self.interpreter.runsource(code_line)
            except Exception as e:
                print(e)
            sys.stdout = stdout
            return buffer.getvalue()

    def list_files(self, args):
        try:
            path = args[0] if args else os.getcwd()
            files = os.listdir(path)
            return "\n".join(files)
        except Exception as e:
            return f"Error: {str(e)}"

    def clear_terminal(self, args):
        self.text.delete(1.0, "end")
        return "Welcome to the Terminal, v0.7"

    def quit_terminal(self, args):
        self.destroy()
        return ""

    def print_working_directory(self, args):
        return os.getcwd()

    def change_directory(self, args):
        if not args:
            return "Error: No directory specified"
        try:
            os.chdir(args[0])
            return f"Changed to {os.getcwd()}"
        except Exception as e:
            return f"Error: {str(e)}"

    def make_directory(self, args):
        if not args:
            return "Error: No directory name specified"
        try:
            os.makedirs(args[0])
            return f"Directory '{args[0]}' created."
        except Exception as e:
            return f"Error: {str(e)}"

    def remove_directory(self, args):
        if not args:
            return "Error: No directory name specified"
        try:
            os.rmdir(args[0])
            return f"Directory '{args[0]}' removed."
        except Exception as e:
            return f"Error: {str(e)}"

    def remove_file(self, args):
        if not args:
            return "Error: No file specified"
        try:
            os.remove(args[0])
            return f"File '{args[0]}' removed."
        except Exception as e:
            return f"Error: {str(e)}"

    def copy_file(self, args):
        if len(args) < 2:
            return "Error: Source and destination required"
        try:
            shutil.copy(args[0], args[1])
            return f"Copied {args[0]} to {args[1]}"
        except Exception as e:
            return f"Error: {str(e)}"

    def move_file(self, args):
        if len(args) < 2:
            return "Error: Source and destination required"
        try:
            shutil.move(args[0], args[1])
            return f"Moved {args[0]} to {args[1]}"
        except Exception as e:
            return f"Error: {str(e)}"

    def cat_file(self, args):
        if not args:
            return "Error: No file specified"
        try:
            with open(args[0], "r") as f:
                return f.read()
        except Exception as e:
            return f"Error: {str(e)}"

    def echo_text(self, args):
        return " ".join(args)

    def show_time(self, args):
        return time.strftime("%H:%M:%S")

    def show_date(self, args):
        return time.strftime("%Y-%m-%d")

    def show_disk_space(self, args):
        try:
            path = args[0] if args else "/"
            t, u, f = shutil.disk_usage(path)
            return f"Total: {t//(2**30)} GB, Used: {u//(2**30)} GB, Free: {f//(2**30)} GB"
        except Exception as e:
            return f"Error: {str(e)}"

    def show_memory_info(self, args):
        try:
            m = psutil.virtual_memory()
            return f"Total: {m.total//(2**30)} GB, Available: {m.available//(2**30)} GB, Used: {m.used//(2**30)} GB"
        except Exception as e:
            return f"Error: {str(e)}"

    def show_uptime(self, args):
        try:
            return str(datetime.timedelta(seconds=int(time.time() - psutil.boot_time())))
        except Exception as e:
            return f"Error: {str(e)}"

    def show_processes(self, args):
        try:
            return "\n".join(f"{p.info['pid']} - {p.info['name']}" for p in psutil.process_iter(['pid', 'name']))
        except Exception as e:
            return f"Error: {str(e)}"

    def kill_process(self, args):
        if not args:
            return "Error: No PID specified"
        try:
            pid = int(args[0])
            psutil.Process(pid).terminate()
            return f"Terminated process {pid}"
        except Exception as e:
            return f"Error: {str(e)}"

    def show_current_user(self, args):
        return getpass.getuser()

    def show_hostname(self, args):
        return platform.node()

    def show_ip_address(self, args):
        try:
            # Cross-platform: fallback to socket if popen fails
            ip = os.popen('hostname -I').read().strip()
            if not ip:
                import socket
                ip = socket.gethostbyname(socket.gethostname())
            return ip
        except Exception as e:
            return f"Error: {str(e)}"

    def show_architecture(self, args):
        return platform.machine()

    def run_python_interpreter(self, args):
        return "Python interactive interpreter not supported in this shell. Please type Python code directly."

    def show_help(self, args):
        return "Supported commands:\n" + ", ".join(sorted(self.commands.keys()))

    def rename_file(self, args):
        if len(args) < 2:
            return "Error: Source and new name required"
        try:
            os.rename(args[0], args[1])
            return f"Renamed {args[0]} to {args[1]}"
        except Exception as e:
            return f"Error: {str(e)}"
