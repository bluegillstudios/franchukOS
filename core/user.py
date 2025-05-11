# Copyright 2025 the FranchukOS project authors. 
# Contributed under the Apache License, Version 2.0.

import os
import getpass

class User:
    @staticmethod
    def get_current_user():
        return getpass.getuser()

    @staticmethod
    def get_home_directory():
        return os.path.expanduser("~")
