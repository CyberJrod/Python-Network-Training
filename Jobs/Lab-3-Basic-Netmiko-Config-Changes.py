"""
Lab 3: Netmiko config changes driven by external files.
- Devices loaded from CSV (default: data/lab3-devices.csv)
- Show commands loaded from JSON (default: data/show-commands.json) with selectable flags
- R51 config loaded from JSON (default: data/lab3-config.json -> r51_config list)
- R52 config loaded from file path (default: data/lab3-r52_eigrp.cfg)
"""

import argparse
import csv
import json
from pathlib import Path
from typing import List, Dict, Any
from netmiko import ConnectHandler

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DEVICES_CSV = ROOT / "data" / "lab3-devices.csv"
DEFAULT_COMMANDS_JSON = ROOT / "data" / "show-commands.json"
DEFAULT_CONFIG_JSON = ROOT / "data" / "lab3-config.json"
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
        print(f"CSV not found at {csv_path}. Provide a valid path with --devices-csv.")
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


def load_lab3_config(config_path: Path) -> Dict[str, Any]:
    default = {
        "r51_config": [
            "router eigrp 100",
            "network 10.0.0.0 0.0.0.255",
        ],
        "r52_config_file": str(ROOT / "data" / "lab3-r52_eigrp.cfg"),
    }
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        merged = {**default, **data}
        return merged
    except Exception as exc:
        print(f"Error reading lab3 config JSON {config_path}: {exc}")
        return default


def main():
    parser = argparse.ArgumentParser(description="Lab 3: Basic Netmiko config changes")
    parser.add_argument("--username", required=True, help="Device username")
    parser.add_argument("--password", required=True, help="Device password")
    parser.add_argument("--devices-csv", default=str(DEFAULT_DEVICES_CSV), help="Path to devices CSV")
    parser.add_argument("--commands-json", default=str(DEFAULT_COMMANDS_JSON), help="Path to JSON with command definitions")
    parser.add_argument("--lab3-config-json", default=str(DEFAULT_CONFIG_JSON), help="Path to JSON with R51/R52 config info")
    parser.add_argument("--r52-config", help="Override path to R52 config file (cfg/text file)")
    parser.add_argument("--push-config", action="store_true", help="Push config to devices")
    parser.add_argument("--push-config-targets", default="all", help="Comma-separated hostnames/IPs to push config to (or 'all'/'none')")
    parser.add_argument("--show-interface-brief", action="store_true", help="Run show ip interface brief")
    parser.add_argument("--show-route", action="store_true", help="Run show ip route")
    parser.add_argument("--show-version", action="store_true", help="Run show version")
    parser.add_argument("--show-eigrp-interfaces", action="store_true", help="Run show ip eigrp interfaces")
    parser.add_argument("--show-eigrp-neighbors", action="store_true", help="Run show ip eigrp neighbors")
    parser.add_argument("--show-eigrp-topology", action="store_true", help="Run show ip eigrp topology")
    args = parser.parse_args()

    devices = load_devices(Path(args.devices_csv))
    if len(devices) < 2:
        print("Need at least two device entries; check the CSV.")
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
    selected_cmds = [commands_map[k] for k in selected_keys if k in commands_map]

    lab3_cfg = load_lab3_config(Path(args.lab3_config_json))
    r51_config = lab3_cfg.get("r51_config") or []
    r52_cfg_file = args.r52_config or lab3_cfg.get("r52_config_file")

    push_enabled = args.push_config
    push_targets = {t.strip().lower() for t in (args.push_config_targets or "").split(",") if t.strip()} if args.push_config_targets else set()
    push_all = push_enabled and args.push_config_targets.strip().lower() == "all"
    push_none = (not push_enabled) or args.push_config_targets.strip().lower() == "none" or not push_targets

    if not r51_config:
        print("No R51 config provided; nothing to push to R51.")
    if not r52_cfg_file:
        print("No R52 config file provided; skipping R52 config push.")

    # ----------------------------------------------
    # Connect to Router 51 without 'with' statement
    # ----------------------------------------------
    r51 = devices[0]
    r51_name = r51.get("hostname") or r51["ip"]
    print(f"\n===== Connecting to {r51_name} ({r51['ip']}) =====")
    r51_conn = {
        "device_type": r51.get("device_type") or DEFAULT_DEVICE_TYPE,
        "host": r51["ip"],
        "username": args.username,
        "password": args.password,
    }
    net_connect = ConnectHandler(**r51_conn)
    should_push_r51 = push_enabled and (push_all or (not push_none and (r51_name.lower() in push_targets or r51["ip"].lower() in push_targets)))
    if should_push_r51 and r51_config:
        output = net_connect.send_config_set(r51_config)
        print("\n>>> Sending config to R51...")
        print(output)
    elif should_push_r51:
        print("Push-config requested but no R51 config provided.")
    if selected_cmds:
        for cmd in selected_cmds:
            output = net_connect.send_command(cmd)
            print(f"\n{r51_name} - {cmd}\n{output}\n")
    net_connect.disconnect()

    # ----------------------------------------------
    # Connect to Router 52 using 'with' statement
    # ----------------------------------------------
    if len(devices) >= 2 and r52_cfg_file:
        r52 = devices[1]
        r52_name = r52.get("hostname") or r52["ip"]
        print(f"\n===== Connecting to {r52_name} ({r52['ip']}) =====")
        r52_conn = {
            "device_type": r52.get("device_type") or DEFAULT_DEVICE_TYPE,
            "host": r52["ip"],
            "username": args.username,
            "password": args.password,
        }
        cfg_path = Path(r52_cfg_file)
        should_push_r52 = push_enabled and (push_all or (not push_none and (r52_name.lower() in push_targets or r52["ip"].lower() in push_targets)))
        if should_push_r52 and not cfg_path.exists():
            print(f"Config file not found: {cfg_path}")
            return
        with ConnectHandler(**r52_conn) as net_connect:
            if should_push_r52 and cfg_path.exists():
                output = net_connect.send_config_from_file(str(cfg_path))
                print("\n>>> Sending config to R52 (from file)...")
                print(output)
            elif should_push_r52:
                print("Push-config requested but no R52 config file provided.")
            if selected_cmds:
                for cmd in selected_cmds:
                    output = net_connect.send_command(cmd)
                    print(f"\n{r52_name} - {cmd}\n{output}\n")
    else:
        print("Skipping R52: missing device entry or config file.")


if __name__ == "__main__":
    main()
