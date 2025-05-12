# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.
# Enhanced Terminal for FranchukOS

import tkinter as tk
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
        self.title("Terminal")
        self.geometry("700x450")
        self.configure(bg="black")

        self.text = tk.Text(self, bg="black", fg="lime", insertbackground="white",
                            font=("Courier New", 11), undo=True, wrap="word")
        self.text.pack(fill="both", expand=True)
        self.text.insert("end", "Terminal\n" + self.PROMPT)
        self.text.bind("<Return>", self.handle_enter)
        self.text.bind("<Up>", self.history_up)
        self.text.bind("<Down>", self.history_down)

        self.cmd_buffer = ""
        self.cmd_history = []
        self.history_index = -1
        self.interpreter = code.InteractiveInterpreter()

        self.commands = {
            "list": self.list_files,
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
            "version": lambda args: "FranchukOS version 29.0.7061.11 (codenamed Denali). Terminal version v0.5.0988",
        }

    def handle_enter(self, event):
        index = self.text.index("insert linestart")
        line = self.text.get(index, "insert lineend").strip()
        if line.startswith(self.PROMPT):
            code_line = line[len(self.PROMPT):].strip()
        else:
            code_line = line.strip()
        self.text.insert("end", "\n")
        self.cmd_history.append(code_line)
        self.history_index = len(self.cmd_history)
        output = self.run_code(code_line)
        if output:
            self.text.insert("end", output.strip() + "\n")
        self.text.insert("end", self.PROMPT)
        self.text.see("end")
        return "break"

    def history_up(self, event):
        if self.cmd_history and self.history_index > 0:
            self.history_index -= 1
            self.replace_current_line(self.cmd_history[self.history_index])
        return "break"

    def history_down(self, event):
        if self.cmd_history and self.history_index < len(self.cmd_history) - 1:
            self.history_index += 1
            self.replace_current_line(self.cmd_history[self.history_index])
        else:
            self.replace_current_line("")
        return "break"

    def replace_current_line(self, text):
        self.text.delete("insert linestart + {}c".format(len(self.PROMPT)), "insert lineend")
        self.text.insert("insert", text)

    def run_code(self, code_line):
        if not code_line:
            return ""
        parts = code_line.split()
        cmd, args = parts[0], parts[1:]

        if cmd in self.commands:
            try:
                return self.commands[cmd](args)
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            # Try as Python code
            stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            try:
                self.interpreter.runsource(code_line)
            except Exception as e:
                print(e)
            sys.stdout = stdout
            return buffer.getvalue()

    # Command Implementations
    def list_files(self, args): return "\n".join(os.listdir(os.getcwd()))
    def clear_terminal(self, args): self.text.delete(1.0, "end"); return "Terminal"
    def quit_terminal(self, args): self.destroy(); return ""
    def print_working_directory(self, args): return os.getcwd()
    def change_directory(self, args): os.chdir(args[0]); return f"Changed to {os.getcwd()}"
    def make_directory(self, args): os.makedirs(args[0]); return f"Directory '{args[0]}' created."
    def remove_directory(self, args): os.rmdir(args[0]); return f"Directory '{args[0]}' removed."
    def remove_file(self, args): os.remove(args[0]); return f"File '{args[0]}' removed."
    def copy_file(self, args): shutil.copy(args[0], args[1]); return f"Copied {args[0]} to {args[1]}"
    def move_file(self, args): shutil.move(args[0], args[1]); return f"Moved {args[0]} to {args[1]}"
    def cat_file(self, args): return open(args[0]).read()
    def echo_text(self, args): return " ".join(args)
    def show_time(self, args): return time.strftime("%H:%M:%S")
    def show_date(self, args): return time.strftime("%Y-%m-%d")
    def show_disk_space(self, args):
        t, u, f = shutil.disk_usage("/")
        return f"Total: {t//(2**30)} GB, Used: {u//(2**30)} GB, Free: {f//(2**30)} GB"
    def show_memory_info(self, args):
        m = psutil.virtual_memory()
        return f"Total: {m.total//(2**30)} GB, Available: {m.available//(2**30)} GB, Used: {m.used//(2**30)} GB"
    def show_uptime(self, args):
        return str(datetime.timedelta(seconds=int(time.time() - psutil.boot_time())))
    def show_processes(self, args):
        return "\n".join(f"{p.info['pid']} - {p.info['name']}" for p in psutil.process_iter(['pid', 'name']))
    def kill_process(self, args):
        pid = int(args[0])
        psutil.Process(pid).terminate()
        return f"Terminated process {pid}"
    def show_current_user(self, args): return getpass.getuser()
    def show_hostname(self, args): return platform.node()
    def show_ip_address(self, args): return os.popen('hostname -I').read().strip()
    def show_architecture(self, args): return platform.architecture()[0]
    def run_python_interpreter(self, args): return "Python interpreter ready. Use 'exit()' to quit."
    def show_help(self, args): return "\n".join(self.commands.keys())
