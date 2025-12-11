from tools.check_reachability_utils import run_ping_check
from tools.inventory_utils import load_devices_from_yaml

devices = load_devices_from_yaml()

ips = []

for device in devices:
    ips.append(device['ip'])

run_ping_check(ips)