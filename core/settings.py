# Copyright 2025 the FranchukOS project authors. 
# Contributed under the Apache License, Version 2.0.

import json
import os

class Settings:
    def __init__(self, path="config/settings.json"):
        self.path = path
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, 'r') as f:
                self.data = json.load(f)

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
