show_commands.pyimport os
import yaml
from netmiko import ConnectHandler


# ----------------------------------------
# Load devices from YAML (simple version)
# ----------------------------------------
def load_devices(filename="devices.yaml"):
    with open(filename) as f:
        data = yaml.safe_load(f)
    return data["devices"]


# ----------------------------------------
# Ping a single IP
# ----------------------------------------
def ping_device(ip):
    response = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")
    return response == 0


# Ping all devices
def check_reachability(devices):
    for dev in devices:
        ip = dev["ip"]
        if ping_device(ip):
            print(f"{ip} is reachable.")
        else:
            print(f"{ip} is NOT reachable.")


# ----------------------------------------
# SSH and run commands
# ----------------------------------------
def connect_and_run_commands(device, commands):
    hostname = device.get("hostname", device["ip"])

    params = {
        "device_type": device["device_type"],
        "host": device["ip"],
        "username": device["username"],
        "password": device["password"],
    }

    try:
        conn = ConnectHandler(**params)

        for cmd in commands:
            output = conn.send_command(cmd)
            print(f"\n===== {hostname} - {cmd} =====\n{output}\n")

        conn.disconnect()

    except Exception as e:
        print(f"\n[ERROR] Failed on {hostname}: {e}\n")


# ----------------------------------------
# Main workflow
# ----------------------------------------
if name == "main":
    devices = load_devices()

    print("=== Reachability Check ===")
    check_reachability(devices)

    commands = [
        "show ip interface brief | exclude unassigned",
        "show version | include Cisco IOS XE Software, Version"
    ]

    print("\n=== Running Show Commands ===")
    for device in devices:
        connect_and_run_commands(device, commands)