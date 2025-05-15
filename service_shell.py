# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import argparse
import sys
import os
import shutil
from service import backup, update, network
update_manager = update
backup_manager = backup
VERSION_FILE = "../rainier/VERSION"
BACKUP_DIR = "backups/"

def backup_os():
    """Creates a backup of the current OS version."""
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        backup_path = os.path.join(BACKUP_DIR, "os_backup.zip")
        backup_manager.create_backup(output_path=backup_path)
        print(f"[✓] Backup successful! Stored at {backup_path}")
    except Exception as e:
        print(f"[!] Backup failed: {e}")

def check_for_updates():
    """Checks for version updates and notifies if available."""
    try:
        current_version = update_manager.get_current_version(VERSION_FILE)
        latest_version = update_manager.get_latest_version_online()

        if current_version != latest_version:
            print(f"[!] Update available! Current: {current_version}, Latest: {latest_version}")
            update_manager.notify_update_available(current_version, latest_version)
        else:
            print("[✓] FranchukOS is up to date.")
    except Exception as e:
        print(f"[!] Update check failed: {e}")

def handle_network():
    """Placeholder for network handling."""
    print("[i] Network service is not required on this version (Denali).")

def main():
    parser = argparse.ArgumentParser(description="Welcome to the FranchukOS Service Shell. If you got here by mistake, it's ok! Just close this window and carry on.")
    parser.add_argument("command", choices=["backup", "check", "network"], help="Service command to run")
    args = parser.parse_args()

    if args.command == "backup":
        backup_os()
    elif args.command == "check":
        check_for_updates()
    elif args.command == "network":
        handle_network()

if __name__ == "__main__":
    main()
