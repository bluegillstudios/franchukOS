# Copyright 2025 the FranchukOS project authors. 
# Contributed under the Apache License, Version 2.0.
# Terminal application for FranchukOS

import tkinter as tk
import code
import sys
import io
import os
import shutil
import platform
import psutil # type: ignore
import datetime

class Terminal(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Terminal")
        self.geometry("600x400")
        self.configure(bg="black")

        self.text = tk.Text(self, bg="black", fg="lime", insertbackground="white", font=("Courier", 10))
        self.text.pack(fill="both", expand=True)
        self.text.insert("end", "Terminal\n>>> ")
        self.text.bind("<Return>", self.handle_enter)

        self.cmd_buffer = ""
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
        }

    def handle_enter(self, event):
        line = self.text.get("insert linestart", "insert lineend").strip(">>> ")
        self.text.insert("end", "\n")
        output = self.run_code(line)
        if output:
            self.text.insert("end", output)
        self.text.insert("end", ">>> ")
        self.text.see("end")
        return "break"

    def run_code(self, code_line):
        # Check if it is a predefined command
        if code_line in self.commands:
            return self.commands[code_line]()
        # Otherwise, treat it as regular Python code
        stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        try:
            self.interpreter.runsource(code_line)
        except Exception as e:
            print(e)
        sys.stdout = stdout
        return buffer.getvalue()

    def list_files(self):
        try:
            return "\n".join(os.listdir(os.getcwd()))  # List files in the current directory
        except Exception as e:
            return f"Error: {str(e)}"

    def clear_terminal(self):
        self.text.delete(1.0, "end")
        self.text.insert("end", "Terminal\n>>> ")

    def quit_terminal(self):
        self.destroy()

    def print_working_directory(self):
        return os.getcwd()

    def change_directory(self, path):
        try:
            os.chdir(path)
            return f"Changed directory to {os.getcwd()}"
        except Exception as e:
            return f"Error: {str(e)}"

    def make_directory(self, dir_name):
        try:
            os.makedirs(dir_name)
            return f"Directory '{dir_name}' created."
        except Exception as e:
            return f"Error: {str(e)}"

    def remove_directory(self, dir_name):
        try:
            os.rmdir(dir_name)
            return f"Directory '{dir_name}' removed."
        except Exception as e:
            return f"Error: {str(e)}"

    def remove_file(self, file_name):
        try:
            os.remove(file_name)
            return f"File '{file_name}' removed."
        except Exception as e:
            return f"Error: {str(e)}"

    def copy_file(self, source, destination):
        try:
            shutil.copy(source, destination)
            return f"Copied from {source} to {destination}"
        except Exception as e:
            return f"Error: {str(e)}"

    def move_file(self, source, destination):
        try:
            shutil.move(source, destination)
            return f"Moved from {source} to {destination}"
        except Exception as e:
            return f"Error: {str(e)}"

    def cat_file(self, file_name):
        try:
            with open(file_name, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error: {str(e)}"

    def echo_text(self, text):
        return text

    def show_time(self):
        return time.strftime("%H:%M:%S")

    def show_date(self):
        return time.strftime("%Y-%m-%d")

    def show_disk_space(self):
        total, used, free = shutil.disk_usage("/")
        return f"Total: {total // (2**30)} GB, Used: {used // (2**30)} GB, Free: {free // (2**30)} GB"

    def show_memory_info(self):
        memory = psutil.virtual_memory()
        return f"Total: {memory.total // (2**30)} GB, Available: {memory.available // (2**30)} GB, Used: {memory.used // (2**30)} GB"

    def show_uptime(self):
        uptime = datetime.timedelta(seconds=int(time.time() - psutil.boot_time()))
        return f"Uptime: {uptime}"

    def show_processes(self):
        processes = "\n".join([f"{p.info['pid']} - {p.info['name']}" for p in psutil.process_iter(['pid', 'name'])])
        return processes

    def kill_process(self, pid):
        try:
            process = psutil.Process(pid)
            process.terminate()
            return f"Terminated process {pid}"
        except Exception as e:
            return f"Error: {str(e)}"

    def show_current_user(self):
        return os.getlogin()

    def show_hostname(self):
        return platform.node()

    def show_ip_address(self):
        return os.popen('hostname -I').read().strip()

    def show_architecture(self):
        return platform.architecture()[0]

    def run_python_interpreter(self):
        return "Entering Python interpreter (type 'exit()' to exit)."

    def show_help(self):
        return "\n".join(self.commands.keys())
