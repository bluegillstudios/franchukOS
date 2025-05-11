# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

def get_current_version(version_file):
    """Reads the current OS version from a file."""
    with open(version_file, "r") as f:
        return f.read().strip()

def get_latest_version_online():
    """
    Placeholder function to simulate online version check.
    Replace this with actual HTTP version check if needed.
    """
    return "29.0.7061.11"  

def notify_update_available(current, latest):
    print(f"[!] A new version of FranchukOS is available: {latest} (current: {current})")
