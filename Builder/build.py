import subprocess
import os
import platform
import shutil

MAIN_FILE = "../rainier.py"
ICON_FILE = "../Assets/icons/franchukos.ico" 
EXE_NAME = "rainier"

def clean():
    for folder in ["build", "dist", "__pycache__"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    spec_file = f"{EXE_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)

def build():
    command = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",  
        f"--name={EXE_NAME}",
        MAIN_FILE
    ]

    if os.path.exists(ICON_FILE):
        command.insert(-1, f"--icon={ICON_FILE}")

    print("Building executable...")
    subprocess.run(command)

if __name__ == "__main__":
    print("Cleaning previous builds...")
    clean()
    build()
    print("\nBuild complete. Executable is in /dist/")