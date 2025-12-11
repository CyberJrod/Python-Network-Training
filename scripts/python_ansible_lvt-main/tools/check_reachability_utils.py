import os
import platform
import subprocess
from tools.inventory_utils import load_devices_from_yaml


def run_ping_check(ips):
    """
    Ping each IP once. Uses platform-appropriate flags to avoid false negatives on Windows.
    """
    is_windows = platform.system().lower().startswith("win")
    count_flag = "-n" if is_windows else "-c"
    # Quiet output; redirect handled by subprocess pipes
    for ip in ips:
        try:
            result = subprocess.run(
                ["ping", count_flag, "1", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
            )
            if result.returncode == 0:
                print(f"{ip} is reachable")
            else:
                print(f"{ip} is NOT reachable")
        except Exception as exc:
            print(f"{ip} is NOT reachable (error: {exc})")
