#----------------------------------------------
# Variables
#----------------------------------------------

hostname1 = "C8K-R51"
hostname2 = "C8K-R52"

c8k51_ip = "10.0.0.51"
c8k52_ip = "10.0.0.52"

username = "admin"
password = "C1sc0123!"

command1 = "show ip interface brief"
command2 = "show ip route"

device_type = "cisco_ios"

eigrp_as = 100

device_ips = ["10.0.0.51", "10.0.0.52"]

commands = ["show ip interface brief", "show ip route"]


# ----------------------------------------------
# Import Modules
# ----------------------------------------------

from netmiko import ConnectHandler


# ----------------------------------------------
# Build per-device connection info from variables
# (ConnectHandler requires Dictionary)
# ----------------------------------------------

c8k51 = {
    "device_type": device_type,
    "host": c8k51_ip,
    "username": username,
    "password": password
}

c8k52 = {
    "device_type": device_type,
    "host": c8k52_ip,
    "username": username,
    "password": password
}


# ----------------------------------------------
# Connect to Router 51 without 'with' statement
# ----------------------------------------------

print(f"\n===== Connecting to {hostname1} ({c8k51_ip}) =====")

# Build config set for R51
r51_config = [
    f"router eigrp {eigrp_as}",
    "network 10.0.0.0 0.0.0.255"
]

# Connect and send config
net_connect = ConnectHandler(**c8k51)

print("\n>>> Sending EIGRP config to R51...")
output = net_connect.send_config_set(r51_config)
print(output)

net_connect.disconnect()


# ----------------------------------------------
# Connect to Router 52 using 'with' statement
# ----------------------------------------------

print(f"\n===== Connecting to {hostname2} ({c8k52_ip}) =====")

# Config file must exist in the same directory:
# r52_eigrp.cfg
#
# Contents:
# router eigrp 100
# network 10.0.0.0 0.0.0.255

with ConnectHandler(**c8k52) as net_connect:
    print("\n>>> Sending EIGRP config to R52 from file...")
    output = net_connect.send_config_from_file("r52_eigrp.cfg")
    print(output)