# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import json
import os
from datetime import datetime

FIRMWARE_TABLE_PATH = "json/table.json"

def load_firmware_table():
    if not os.path.exists(FIRMWARE_TABLE_PATH):
        with open(FIRMWARE_TABLE_PATH, "w") as f:
            json.dump({}, f)
    with open(FIRMWARE_TABLE_PATH, "r") as f:
        return json.load(f)

def save_firmware_table(table):
    with open(FIRMWARE_TABLE_PATH, "w") as f:
        json.dump(table, f, indent=4)

def register_firmware(device_id, firmware_version):
    table = load_firmware_table()
    table[device_id] = {
        "version": firmware_version,
        "status": "installed",
        "timestamp": datetime.utcnow().isoformat() # FIXME: Use a better timestamp format since utcnow() is deprecated. Fix by M31
    }
    save_firmware_table(table)

def upgrade_firmware(device_id, new_version):
    table = load_firmware_table()
    if device_id in table:
        table[device_id]["previous_version"] = table[device_id]["version"]
        table[device_id]["version"] = new_version
        table[device_id]["status"] = "upgraded"
        table[device_id]["timestamp"] = datetime.utcnow().isoformat()
        save_firmware_table(table)
        return True
    return False

def rollback_firmware(device_id):
    table = load_firmware_table()
    if device_id in table and "previous_version" in table[device_id]:
        table[device_id]["version"] = table[device_id]["previous_version"]
        table[device_id]["status"] = "rolled_back"
        table[device_id]["timestamp"] = datetime.utcnow().isoformat()
        save_firmware_table(table)
        return True
    return False

def get_firmware_info(device_id):
    table = load_firmware_table()
    return table.get(device_id)

def list_all_firmware():
    return load_firmware_table()
