# Copyright 2025 the FranchukOS project authors.
# Contributed under the Apache License, Version 2.0.

import shutil
import os

def create_backup(output_path="backups/os_backup.zip"):
    """Compresses the FranchukOS directory into a zip file."""
    base_dir = "../../franchukos"  
    shutil.make_archive(output_path.replace(".zip", ""), 'zip', base_dir)
