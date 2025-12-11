import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

devices = [
    {
        "host": "10.0.0.51",
        "port": 443,
        "username": "admin",
        "password": "C1sc0123!"
    },
    {
        "host": "10.0.0.52",
        "port": 443,
        "username": "admin",
        "password": "C1sc0123!"
    }
]

interface_name = "GigabitEthernet1"
interface_description = "Configured via RESTCONF"

headers = {
    "Content-Type": "application/yang-data+json",
    "Accept": "application/yang-data+json"
}

payload = {
    "ietf-interfaces:interface": {
        "name": interface_name,
        "description": interface_description,
        "type": "iana-if-type:ethernetCsmacd",
        "enabled": True
    }
}

for device in devices:
    url = (
        f"https://{device['host']}:{device['port']}"
        f"/restconf/data/ietf-interfaces:interfaces/interface={interface_name}"
    )

    print(f"\nPushing description to {interface_name} on {device['host']} ...")

    try:
        response = requests.patch(
            url,
            headers=headers,
            auth=(device["username"], device["password"]),
            data=json.dumps(payload),
            verify=False,
            timeout=5,   # <-- explicit timeout in seconds
        )
    except requests.exceptions.ConnectTimeout:
        print(f"❌ Could not reach {device['host']} on port {device['port']} (connect timeout)")
        continue
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error talking to {device['host']}: {e}")
        continue

    if response.status_code in [200, 201, 204]:
        print(f"✅ Successfully updated description on {device['host']}")
    else:
        print(f"❌ Failed on {device['host']} (status {response.status_code})")
        print(f"Response: {response.text}")
