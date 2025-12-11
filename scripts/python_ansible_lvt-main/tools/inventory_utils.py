import os
import yaml

def load_devices_from_yaml(filename="devices.yaml"):
    # Folder path where YAML file is located
    base = os.path.dirname(__file__)
    path = os.path.join(base, filename)
    with open(path, "r") as file:
        data = yaml.safe_load(file)

    return data['devices']