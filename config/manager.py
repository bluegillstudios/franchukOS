# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import json
import os

CONFIG_PATH = "config/settings.json"
PROFILES_PATH = "config/profiles.json"

def load_config():
    """Load the system settings from the settings.json file."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as file:
            return json.load(file)
    else:
        # Let's return default here.
        return {
            "theme": "light",
            "wallpaper": "assets/backgrounds/wallpaper.png"
        }

def save_config(config_data):
    """Save the system settings to the settings.json file."""
    with open(CONFIG_PATH, "w") as file:
        json.dump(config_data, file, indent=4)

def load_profiles():
    """Load user profiles from the profiles.json file."""
    if os.path.exists(PROFILES_PATH):
        with open(PROFILES_PATH, "r") as file:
            return json.load(file)
    else:
        # Default profiles.
        return {
            "users": [
                {
                    "username": "admin",
                    "password": "hashedpassword"
                }
            ]
        }

def save_profiles(profiles_data):
    """Save user profiles to the profiles.json file."""
    with open(PROFILES_PATH, "w") as file:
        json.dump(profiles_data, file, indent=4)
