# Copyright 2025 the FranchukOS project authors. 
# Contributed under the Apache License, Version 2.0.

import os
import shutil

class FileSystem:
    @staticmethod
    def list_directory(path):
        try:
            return os.listdir(path)
        except FileNotFoundError:
            return f"Directory {path} not found."
    
    @staticmethod
    def create_file(path, content=""):
        try:
            with open(path, 'w') as file:
                file.write(content)
            return f"File {path} created successfully."
        except Exception as e:
            return f"Error creating file: {e}"
    
    @staticmethod
    def delete_file(path):
        try:
            os.remove(path)
            return f"File {path} deleted successfully."
        except FileNotFoundError:
            return f"File {path} not found."
        except Exception as e:
            return f"Error deleting file: {e}"
    
    @staticmethod
    def move_file(source, destination):
        try:
            shutil.move(source, destination)
            return f"File moved from {source} to {destination}."
        except Exception as e:
            return f"Error moving file: {e}"
    @staticmethod
    def read_file(path):
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

    @staticmethod
    def copy_file(source, destination):
        try:
            shutil.copy(source, destination)
            return f"Copied from {source} to {destination}"
        except Exception as e:
            return f"Error copying file: {e}"



