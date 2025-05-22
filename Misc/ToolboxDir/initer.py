import os
import sys

MODULE_DIRS = [
    "apps",
    "gui",
    "service",
    "core",
    "config"
]

def create_init_files():
    for directory in MODULE_DIRS:
        init_path = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write("# Init for " + directory + "\n")
            print(f"Created: {init_path}")
        else:
            print(f"Already exists: {init_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        create_init_files()
    else:
        print("Usage: python initer.py start")
