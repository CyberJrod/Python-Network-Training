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


# ----------------------------------------------
# Build per-device connection info from variables
# (ConnectHandler requires Dictionary)
# ----------------------------------------------

c8k51 = {
}

c8k52 = {
}


# ----------------------------------------------
# Connect to Router 51 without 'with' statement
# ----------------------------------------------

print(f"\n===== Connecting to {hostname1} ({c8k51_ip}) =====")

# ----------------------------------------------
# Connect to Router 52 using 'with' statement
# ----------------------------------------------

print(f"\n===== Connecting to {hostname2} ({c8k52_ip}) =====")



