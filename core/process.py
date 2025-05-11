import psutil
import subprocess

class ProcessManager:
    @staticmethod
    def list_processes():
        """Returns a list of tuples: (pid, name)"""
        return [(p.pid, p.name()) for p in psutil.process_iter(['name'])]

    @staticmethod
    def kill_process(pid):
        """Attempts to kill a process by PID"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return f"Process {pid} terminated."
        except psutil.NoSuchProcess:
            return f"No process found with PID {pid}."
        except Exception as e:
            return f"Error terminating process: {e}"

    @staticmethod
    def launch_process(command):
        """Launches a process via command string or list"""
        try:
            subprocess.Popen(command if isinstance(command, list) else command.split())
            return f"Process '{command}' launched."
        except Exception as e:
            return f"Error launching process: {e}"
