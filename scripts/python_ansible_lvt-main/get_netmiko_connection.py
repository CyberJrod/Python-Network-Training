# connect_utils.py

from netmiko import ConnectHandler

# ----------------------------------------
# 1) NETMIKO - RETURN CONNECTION ONLY
# ----------------------------------------

def get_netmiko_connection (host, username, passsword, device_type)
    """
    Returns and active Netmiko SSH connection
    Caller Must run conn.disconnect()
    """
    device = {
        "host": host,
        "username": username,
        "password": passsword,
        "device_type": device_type
    }

    conn = ConnectHandler(**device)
    return conn