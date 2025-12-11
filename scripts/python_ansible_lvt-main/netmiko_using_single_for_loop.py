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

# List of device objects with hostname for printing
devices = [
    {"hostname": hostname1, "ip": c8k51_ip, "info": c8k51},
    {"hostname": hostname2, "ip": c8k52_ip, "info": c8k52}
]

# ------------------------------------------------------
# Connect to Routers using For Loop and 'with' statement
# ------------------------------------------------------

for device in devices:

    print(f"\n===== Connecting to {device['hostname']} ({device['ip']}) =====")

    with ConnectHandler(**device["info"]) as net_connect:

        # First command
        output = net_connect.send_command(command1)
        print(f"\n{device['hostname']} - {command1}\n{output}\n")

        # Second command
        output = net_connect.send_command(command2)
        print(f"\n{device['hostname']} - {command2}\n{output}\n")