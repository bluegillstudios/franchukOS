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
import tarfile
import ar
import tempfile
import subprocess
import threading

# --- FSL Integration ---
from fsl import core as fsl_core
from fsl import manager as fsl_manager
from fsl import shell as fsl_shell


class Terminal(tk.Toplevel):
    PROMPT = ">>> "

    THEMES = {
        "Dark": {"bg": "#1e1e1e", "fg": "#00ff00", "insertbackground": "white", "prompt_fg": "#00ff00"},
        "Light": {"bg": "#f8f8f8", "fg": "#222222", "insertbackground": "black", "prompt_fg": "#0055aa"},
        "Solarized": {"bg": "#002b36", "fg": "#839496", "insertbackground": "#93a1a1", "prompt_fg": "#b58900"},
        "Monokai": {"bg": "#272822", "fg": "#f8f8f2", "insertbackground": "#f8f8f0", "prompt_fg": "#a6e22e"},
        "Gruvbox": {"bg": "#282828", "fg": "#ebdbb2", "insertbackground": "#fbf1c7", "prompt_fg": "#fabd2f"},
        "Dracula": {"bg": "#282a36", "fg": "#f8f8f2", "insertbackground": "#f8f8f2", "prompt_fg": "#bd93f9"},
        "Nord": {"bg": "#2e3440", "fg": "#d8dee9", "insertbackground": "#eceff4", "prompt_fg": "#88c0d0"},
        "High Contrast": {"bg": "#000000", "fg": "#ffffff", "insertbackground": "#ffffff", "prompt_fg": "#ffff00"}
    }

    def __init__(self, master=None, theme="Dark"):
        super().__init__(master)
        self.title("Terminal v1.1.0")
        self.geometry("800x500")
        self.current_theme = theme
        self.configure(bg=self.THEMES[theme]["bg"])
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TText", background=self.THEMES[theme]["bg"], foreground=self.THEMES[theme]["fg"], font=("Consolas", 11))

        self.text = tk.Text(self, bg=self.THEMES[theme]["bg"], fg=self.THEMES[theme]["fg"], insertbackground=self.THEMES[theme]["insertbackground"],
                            font=("Consolas", 11), undo=True, wrap="word",
                            borderwidth=0, highlightthickness=0, padx=10, pady=10)
        self.text.pack(fill="both", expand=True, padx=10, pady=10)
        self.text.insert("end", "Welcome to the FranchukOS Terminal, v1.1.0\n")
        self.text.insert("end", "If you got here by mistake, it's ok! Just close this tab and carry on.\n")
        self.text.insert("end", self.PROMPT, "prompt")
        self.text.tag_configure("prompt", foreground=self.THEMES[theme]["prompt_fg"])
        self.text.tag_configure("welcome", foreground=self.THEMES[theme]["fg"])
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
            "version": lambda args: "FranchukOS version 34.2.9 (codenamed Mojave). Terminal version v1.1.4.",
            "rename": self.rename_file,
            "theme": self.set_theme_command,
            "debinstall": self.install_deb_package,
            "debrun": self.run_deb_binary,
            "run": self.run_python_app,
            # --- FSL command integration ---
            "fsl": self.run_fsl_command,
        }

    # --- Theme handling ---
    def set_theme(self, theme):
        if theme not in self.THEMES:
            return
        self.current_theme = theme
        colors = self.THEMES[theme]
        self.configure(bg=colors["bg"])
        self.text.config(bg=colors["bg"], fg=colors["fg"], insertbackground=colors["insertbackground"])
        self.text.tag_configure("prompt", foreground=colors["prompt_fg"])
        self.text.tag_configure("welcome", foreground=colors["fg"])

    def set_theme_command(self, args):
        if not args or args[0] not in self.THEMES:
            return "Available themes: " + ", ".join(self.THEMES.keys())
        self.set_theme(args[0])
        return f"Theme set to {args[0]}"

    # --- Input handling ---
    def handle_enter(self, event=None):
        index = self.text.index("insert linestart")
        line = self.text.get(index, "insert lineend")
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
        self.text.insert("end", self.PROMPT, "prompt")
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
        line_start = self.text.index("insert linestart")
        prompt_len = len(self.PROMPT)
        self.text.delete(f"{line_start}+{prompt_len}c", f"{line_start} lineend")
        self.text.insert(f"{line_start}+{prompt_len}c", text)

    # --- Command dispatcher ---
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
            stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            try:
                self.interpreter.runsource(code_line)
            except Exception as e:
                print(e)
            sys.stdout = stdout
            return buffer.getvalue()

    # --- File and system commands ---
    def list_files(self, args):
        try:
            path = args[0] if args else os.getcwd()
            return "\n".join(os.listdir(path))
        except Exception as e:
            return f"Error: {str(e)}"

    def clear_terminal(self, args):
        self.text.delete(1.0, "end")

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
            ip = os.popen('hostname -I').read().strip()
            if not ip:
                import socket
                ip = socket.gethostbyname(socket.gethostname())
            return ip
        except Exception as e:
            return f"Error: {str(e)}"

    def show_architecture(self, args):
        return platform.machine()

    # --- Python commands ---
    def run_python_interpreter(self, args):
        self.text.insert("end", "\nEntering Python interactive interpreter. Type 'exit()' to leave.\n")
        self.text.insert("end", ">>> ", "prompt")
        self.text.see("end")
        buffer = ""
        while True:
            self.text.mark_set("insert", "end")
            self.text.focus_set()
            self.wait_variable(tk.BooleanVar())
            index = self.text.index("insert linestart")
            line = self.text.get(index, "insert lineend")
            if line.startswith(self.PROMPT):
                code_line = line[len(self.PROMPT):].strip()
            else:
                code_line = line.strip()
            self.text.insert("end", "\n")
            if code_line == "exit()":
                self.text.insert("end", "Leaving Python interpreter.\n")
                self.text.insert("end", self.PROMPT, "prompt")
                self.text.see("end")
                break
            stdout = sys.stdout
            sys.stdout = buffer_io = io.StringIO()
            try:
                self.interpreter.runsource(code_line)
            except Exception as e:
                print(e)
            sys.stdout = stdout
            output = buffer_io.getvalue()
            if output:
                self.text.insert("end", output)
            self.text.insert("end", ">>> ", "prompt")
            self.text.see("end")
        return ""

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

    # --- DEB package support ---
    def install_deb_package(self, args):
        if not args:
            return "Usage: debinstall <path-to-deb> [appname]"
        deb_path = args[0]
        app_name = args[1] if len(args) > 1 else os.path.splitext(os.path.basename(deb_path))[0]
        install_dir = os.path.join(os.getcwd(), f"{app_name}_extracted")
        os.makedirs(install_dir, exist_ok=True)
        try:
            with open(deb_path, 'rb') as f:
                archive = ar.Archive(f)
                for entry in archive:
                    fname = entry.name.decode() if isinstance(entry.name, bytes) else entry.name
                    if fname.startswith('data.tar'):
                        ext = fname.split('.')[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_tar:
                            temp_tar.write(entry.data)
                            temp_tar_path = temp_tar.name
                        with tarfile.open(temp_tar_path, 'r:*') as tarf:
                            tarf.extractall(install_dir)
                        os.remove(temp_tar_path)
                        return f"Extracted to {install_dir}"
            return "No data.tar.* found in deb."
        except Exception as e:
            return f"Error extracting deb: {e}"

    def run_deb_binary(self, args):
        if not args:
            return "Usage: debrun <extracted-folder> [binaryname]"
        folder = args[0]
        bin_dir = os.path.join(folder, "usr", "bin")
        if not os.path.isdir(bin_dir):
            return f"No usr/bin directory found in {folder}"
        binaries = [f for f in os.listdir(bin_dir) if os.path.isfile(os.path.join(bin_dir, f))]
        if not binaries:
            return "No binaries found in usr/bin."
        binary = args[1] if len(args) > 1 and args[1] in binaries else binaries[0]
        binary_path = os.path.join(bin_dir, binary)
        try:
            if platform.system() == "Windows":
                subprocess.Popen(["wsl", binary_path])
            else:
                subprocess.Popen([binary_path])
            return f"Running {binary_path}"
        except Exception as e:
            return f"Error running binary: {e}"

    def run_python_app(self, args):
        if not args:
            return "Usage: run <script.py> [args...]"
        script = args[0]
        script_args = args[1:]
        if not os.path.isfile(script):
            return f"Error: File '{script}' not found."
        try:
            old_argv = sys.argv
            sys.argv = [script] + script_args
            with open(script, "r") as f:
                code_str = f.read()
            script_globals = {"__name__": "__main__", "__file__": script}
            exec(compile(code_str, script, "exec"), script_globals)
            sys.argv = old_argv
            return f"Executed {script}"
        except Exception as e:
            sys.argv = old_argv
            return f"Error running {script}: {e}"

    # --- FSL integration ---
    def run_fsl_command(self, args):
        if not args:
            return "Usage: fsl <list|install|run> [distro_name]"

        cmd = args[0]
        cmd_args = args[1:] if len(args) > 1 else []

        buffer = io.StringIO()
        stdout = sys.stdout
        sys.stdout = buffer
        try:
            if cmd == "list":
                fsl_manager.list_distros()
            elif cmd == "install":
                if not cmd_args:
                    print("Specify a distro to install.")
                else:
                    fsl_manager.install_distro(cmd_args[0])
            elif cmd == "run":
                if not cmd_args:
                    print("Specify a distro to run.")
                else:
                    distro_name = cmd_args[0]
                    t = threading.Thread(target=fsl_shell.run_distro, args=(distro_name,))
                    t.start()
                    print(f"Launching {distro_name}...")
            else:
                print("Unknown fsl command. Available: list, install, run")
        except Exception as e:
            print(f"FSL error: {str(e)}")
        finally:
            sys.stdout = stdout
        return buffer.getvalue()