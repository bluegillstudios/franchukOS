import sys
from firmupd import (
    register_firmware,
    upgrade_firmware,
    rollback_firmware,
    get_firmware_info,
    list_all_firmware
)

def print_menu():
    print("\nFirmware mgr shell. Select an option. If you wish to exit and boot up franchukOS, type '6.' and boot the file `rainier.py`")
    print("====================")
    print("1. Register firmware")
    print("2. Upgrade firmware")
    print("3. Rollback firmware")
    print("4. Get firmware info")
    print("5. List all firmware")
    print("6. Exit")

def main():
    while True:
        print_menu()
        choice = input("Enter (1-6): ").strip()

        if choice == "1":
            device_id = input("Enter device ID: ").strip()
            version = input("Enter firmware version: ").strip()
            register_firmware(device_id, version)
            print(f"Firmware registered for device {device_id} with version {version}.")

        elif choice == "2":
            device_id = input("Enter device ID: ").strip()
            new_version = input("Enter new firmware version: ").strip()
            if upgrade_firmware(device_id, new_version):
                print(f"Firmware upgraded to version {new_version} for device {device_id}.")
            else:
                print("Device not found. Cannot upgrade.")

        elif choice == "3":
            device_id = input("Enter device ID: ").strip()
            if rollback_firmware(device_id):
                print(f"Firmware rolled back for device {device_id}.")
            else:
                print("Rollback failed. Device not found or no previous version available.")

        elif choice == "4":
            device_id = input("Enter device ID: ").strip()
            info = get_firmware_info(device_id)
            if info:
                print(f"Device ID: {device_id}")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            else:
                print("Device not found.")

        elif choice == "5":
            all_fw = list_all_firmware()
            if not all_fw:
                print("No firmware registered.")
            else:
                print("Registered Firmware:")
                for device, data in all_fw.items():
                    print(f"Device: {device}")
                    for key, value in data.items():
                        print(f"  {key}: {value}")
                    print("-" * 20)

        elif choice == "6":
            print("Exiting Firmware Manager CLI.")
            sys.exit(0)

        else:
            print("Invalid choice. Please select a number between 1 and 6.")

if __name__ == "__main__":
    main()