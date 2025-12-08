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

devices_dict = {
    "device1": {
        "device_type": "cisco_ios", 
        "ip": c8k51_ip, 
        "hostname": hostname1, 
        "username": username, 
        "password": password
    },
    "device2": {
        "device_type": "cisco_ios", 
        "ip": c8k52_ip, 
        "hostname": hostname2, 
        "username": username, 
        "password": password
    }
}

devices_list = [
    {
        "device_type": "cisco_ios",
        "ip": c8k51_ip, 
        "hostname": hostname1, 
        "username": username, 
        "password": password
        }, 
        {
            "device_type": "cisco_ios", 
            "ip": c8k52_ip, 
            "hostname": hostname2, 
            "username": username, 
            "password": password
        }
]



#----------------------------------------------
# Print Statements
#----------------------------------------------

print ("The hostname of the router is", hostname1)
print (f"The hostname of the router is {hostname2}")
print ("The hostname of the router is", hostname1, "and the IP is", c8k51_ip)
print (f"The hostname of the router is {hostname2} and the IP is {c8k52_ip}")
print (command1, ",", command2)
print (f"{command1}, {command2}")
print ("AS is:", eigrp_as, "and type is:", type(eigrp_as))
print (f"The IP address of {hostname1} is {device_ips[0]}")
print (f"The IP address of {devices_dict['device1']['hostname']} is {devices_dict['device1']['ip']}")
print (f"The IP address of {devices_list[1]['hostname']} is {devices_list[1]['ip']}")


