# Copyright 2025 the Wallace project authors. The main system core for the FranchukOS project.
# Contributed under the Apache License, Version 2.0.
# System monitoring module for FranchukOS for versions Rainier and above.

import psutil
import platform
import time
import datetime

def get_system_stats():
    """Return a dictionary of current system statistics."""
    cpu_percent = psutil.cpu_percent(percpu=True)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time

    stats = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "cpu_percent_per_core": cpu_percent,
        "cpu_percent_avg": sum(cpu_percent) / len(cpu_percent),
        "memory_total": memory.total,
        "memory_used": memory.used,
        "memory_percent": memory.percent,
        "disk_total": disk.total,
        "disk_used": disk.used,
        "disk_percent": disk.percent,
        "uptime": str(uptime).split('.')[0]  # HH:MM:SS
    }
    return stats

def get_process_list():
    """Return a list of running processes with basic details."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu_percent": proc.info['cpu_percent'],
                "memory_percent": round(proc.info['memory_percent'], 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)

def kill_process(pid):
    """Attempt to terminate a process by PID."""
    try:
        p = psutil.Process(pid)
        p.terminate()
        return True
    except Exception:
        return False