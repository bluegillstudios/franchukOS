import platform
import psutil
import shutil

class SystemInfo:
    @staticmethod
    def get_os_info():
        return {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }

    @staticmethod
    def get_cpu_info():
        return {
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "usage_percent": psutil.cpu_percent(interval=1)
        }

    @staticmethod
    def get_memory_info():
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "percent_used": mem.percent
        }

    @staticmethod
    def get_disk_info():
        disk = shutil.disk_usage("/")
        return {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "percent_used": round(disk.used / disk.total * 100, 2)
        }
