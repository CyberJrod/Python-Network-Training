"""
Lab 6: Netmiko with error handling using nested loops.
- Devices loaded from CSV (default: data/lab6-devices.csv)
- Commands loaded from JSON (default: data/show-commands.json)
- Username/password from CLI (Streamlit passes these); if missing, prompts for them (password hidden).
- Wraps connections and command execution in try/except to continue on errors.
"""

import argparse
import csv
import json
from getpass import getpass
from pathlib import Path
from typing import List, Dict, Any
from netmiko import ConnectHandler

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CSV = ROOT / "data" / "lab6-devices.csv"
DEFAULT_COMMANDS_JSON = ROOT / "data" / "show-commands.json"
DEFAULT_DEVICE_TYPE = "cisco_ios"
DEFAULT_HOSTNAMES = ["C8K-R51", "C8K-R52"]


def load_devices(csv_path: Path) -> List[Dict[str, Any]]:
    devices: List[Dict[str, Any]] = []
    try:
        with csv_path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                for row in reader:
                    ip = (row.get("ip") or row.get("device_ips") or "").strip()
                    if not ip:
                        continue
                    hostname = (row.get("hostname") or "").strip()
                    device_type = (row.get("device_type") or DEFAULT_DEVICE_TYPE).strip()
                    devices.append({
                        "hostname": hostname,
                        "ip": ip,
                        "device_type": device_type or DEFAULT_DEVICE_TYPE,
                    })
            if not devices:
                f.seek(0)
                reader2 = csv.reader(f)
                for idx, row in enumerate(reader2):
                    if not row:
                        continue
                    val = row[0].strip()
                    if idx == 0 and val.lower() in ("device_ips", "ip"):
                        continue
                    if val:
                        hostname = DEFAULT_HOSTNAMES[idx] if idx < len(DEFAULT_HOSTNAMES) else f"device{idx+1}"
                        devices.append({
                            "hostname": hostname,
                            "ip": val,
                            "device_type": DEFAULT_DEVICE_TYPE,
                        })
    except FileNotFoundError:
        print(f"CSV not found at {csv_path}. Provide a valid path with --csv-path.")
    except Exception as exc:
        print(f"Error reading CSV {csv_path}: {exc}")
    return devices


def load_commands(commands_path: Path) -> Dict[str, str]:
    default_cmds = {
        "show_interface_brief": "show ip interface brief",
        "show_route": "show ip route",
        "show_version": "show version",
        "show_eigrp_interfaces": "show ip eigrp interfaces",
        "show_eigrp_neighbors": "show ip eigrp neighbors",
        "show_eigrp_topology": "show ip eigrp topology",
    }
    try:
        data = json.loads(commands_path.read_text(encoding="utf-8"))
        cmds = data.get("commands", {})
        merged = {**default_cmds, **{k: v for k, v in cmds.items() if isinstance(v, str)}}
        return merged
    except Exception as exc:
        print(f"Error reading commands JSON {commands_path}: {exc}")
        return default_cmds


def main():
    parser = argparse.ArgumentParser(description="Lab 6: Netmiko with error handling")
    parser.add_argument("--username", help="Device username")
    parser.add_argument("--password", help="Device password")
    parser.add_argument("--csv-path", default=str(DEFAULT_CSV), help="Path to CSV with device info")
    parser.add_argument("--commands-json", default=str(DEFAULT_COMMANDS_JSON), help="Path to JSON with command definitions")
    parser.add_argument("--show-interface-brief", action="store_true", help="Run show ip interface brief")
    parser.add_argument("--show-route", action="store_true", help="Run show ip route")
    parser.add_argument("--show-version", action="store_true", help="Run show version")
    parser.add_argument("--show-eigrp-interfaces", action="store_true", help="Run show ip eigrp interfaces")
    parser.add_argument("--show-eigrp-neighbors", action="store_true", help="Run show ip eigrp neighbors")
    parser.add_argument("--show-eigrp-topology", action="store_true", help="Run show ip eigrp topology")
    args = parser.parse_args()

    username = args.username or input("Username: ")
    password = args.password or getpass("Password: ")

    devices = load_devices(Path(args.csv_path))
    if not devices:
        print("No device entries loaded; nothing to do.")
        return

    commands_map = load_commands(Path(args.commands_json))
    selected_keys = []
    if args.show_interface_brief:
        selected_keys.append("show_interface_brief")
    if args.show_route:
        selected_keys.append("show_route")
    if args.show_version:
        selected_keys.append("show_version")
    if args.show_eigrp_interfaces:
        selected_keys.append("show_eigrp_interfaces")
    if args.show_eigrp_neighbors:
        selected_keys.append("show_eigrp_neighbors")
    if args.show_eigrp_topology:
        selected_keys.append("show_eigrp_topology")
    if not selected_keys:
        print("No commands selected; nothing to run.")
        return

    selected_cmds = [commands_map[k] for k in selected_keys if k in commands_map]

    # Error-handled nested loops
    for device in devices:
        name = device.get("hostname") or device["ip"]
        print(f"\n===== Connecting to {name} ({device['ip']}) =====")
        conn = {
            "device_type": device.get("device_type") or DEFAULT_DEVICE_TYPE,
            "host": device["ip"],
            "username": username,
            "password": password,
        }
        try:
            with ConnectHandler(**conn) as net_connect:
                for cmd in selected_cmds:
                    try:
                        output = net_connect.send_command(cmd)
                        print(f"\n{name} - {cmd}\n{output}\n")
                    except Exception as cmd_exc:
                        print(f"Error running '{cmd}' on {name}: {cmd_exc}")
        except Exception as conn_exc:
            print(f"Error connecting to {name} ({device['ip']}): {conn_exc}")


if __name__ == "__main__":
    main()
