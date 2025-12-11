# connect_utils.py

from netmiko import ConnectHandler

# ----------------------------------------
# 1) NETMIKO - RETURN CONNECTION ONLY
# ----------------------------------------

def get_netmiko_connection(device_type, host, username, password, device_type):
    """
    Returns an active Netmiko SSH Connection
    Caller must run conn.disconnect() when done
    """

    device = {
        "device_type": device_type,
        "host": host,
        "username": username,
        "password": password
    }

    conn = ConnectHandler
    return conn
