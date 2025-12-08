#----------------------------------------------
# Variables
#----------------------------------------------

hostname1 = "C8K-R51"
hostname2 = "C8K-R52"

command1 = "show ip interface brief"
command2 = "show ip route"
command3 = "show version"

device_type = "cisco_ios"

eigrp_as = 100

commands = ["show ip interface brief", "show ip route"]



# ----------------------------------------------
# Import Modules
# ----------------------------------------------

import argparse
import csv
from pathlib import Path
from netmiko import ConnectHandler

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "data" / "lab2.csv"

# ----------------------------------------------
# Build per-device connection info from variables
# (ConnectHandler requires Dictionary)
# ----------------------------------------------

base_conn = {
    "device_type": device_type,
}


def load_device_ips(csv_path: Path):
    """
    Loads IPs from a CSV. Accepts either:
    - Headered CSV with column 'device_ips'
    - Plain single-column CSV (first row may be header and will be skipped)
    """
    ips = []
    try:
        with csv_path.open(newline="", encoding="utf-8-sig") as f:
            try:
                reader = csv.DictReader(f)
                # If header missing, DictReader.fieldnames is None
                if reader.fieldnames:
                    for row in reader:
                        ip = row.get("device_ips") or ""
                        if ip.strip():
                            ips.append(ip.strip())
                if not ips:
                    # Fallback to plain rows (ignore header-like first row)
                    f.seek(0)
                    reader2 = csv.reader(f)
                    for idx, row in enumerate(reader2):
                        if not row:
                            continue
                        val = row[0].strip()
                        if idx == 0 and val.lower() == "device_ips":
                            continue
                        if val:
                            ips.append(val)
            except Exception as exc_inner:
                print(f"Error parsing CSV {csv_path}: {exc_inner}")
    except FileNotFoundError:
        print(f"CSV not found at {csv_path}. Provide a valid path with --csv-path.")
    except Exception as exc:
        print(f"Error reading CSV {csv_path}: {exc}")
    return ips


def main():
    parser = argparse.ArgumentParser(description="Lab 2: Basic Netmiko connection")
    parser.add_argument("--username", required=True, help="Device username")
    parser.add_argument("--password", required=True, help="Device password")
    parser.add_argument("--csv-path", default=str(DEFAULT_CSV), help="Path to CSV with device IPs (header: device_ips)")
    parser.add_argument("--show-interface-brief", action="store_true", help="Run show ip interface brief")
    parser.add_argument("--show-route", action="store_true", help="Run show ip route")
    parser.add_argument("--show-version", action="store_true", help="Run show version")
    args = parser.parse_args()

    device_ips = load_device_ips(Path(args.csv_path))
    if not device_ips:
        print("No device IPs loaded; nothing to do.")
        return

    selected_cmds = []
    if args.show_interface_brief:
        selected_cmds.append(command1)
    if args.show_route:
        selected_cmds.append(command2)
    if args.show_version:
        selected_cmds.append(command3)

    if not selected_cmds:
        print("No commands selected; nothing to run.")
        return

    base = {**base_conn, "username": args.username, "password": args.password}
    hostnames = [hostname1, hostname2]
    devices = []
    for idx, ip in enumerate(device_ips):
        name = hostnames[idx] if idx < len(hostnames) else f"device{idx+1}"
        devices.append({"hostname": name, "ip": ip, "info": {**base, "host": ip}})

    # ----------------------------------------------
    # Connect to Router 51 without 'with' statement
    # ----------------------------------------------
    first = devices[0]
    print(f"\n===== Connecting to {first['hostname']} ({first['ip']}) =====")
    net_connect = ConnectHandler(**first["info"])
    for cmd in selected_cmds:
        output = net_connect.send_command(cmd)
        print(f"\n{first['hostname']} - {cmd}\n{output}\n")
    net_connect.disconnect()

    # ----------------------------------------------
    # Connect to remaining routers using 'with' statement
    # ----------------------------------------------
    for device in devices[1:]:
        print(f"\n===== Connecting to {device['hostname']} ({device['ip']}) =====")
        with ConnectHandler(**device["info"]) as net_connect:
            for cmd in selected_cmds:
                output = net_connect.send_command(cmd)
                print(f"\n{device['hostname']} - {cmd}\n{output}\n")


if __name__ == "__main__":
    main()
