import json
from typing import List, Dict
import os

from bleak import BleakClient

from src.loaders.config_error import ConfigError
from src.loaders.device_loader import DeviceLoader
from src.helpers import format_config_name

class ConfigLoader():
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.config = self.load_config()
        self.device_files = [f"{conf}.config" for conf in self.get_device_names()]
        self.device_configs = self.load_device_configs()

    def load_config(self):
        with open(self.config_path, "r") as infile:
            return json.loads(infile.read())
        
    def save_config(self):
        with open(self.config_path, "w") as outfile:
            outfile.write(json.dumps(self.config))

    def get_config_name(self) -> str:
        name = self.config.get("name")
        if not name:
            raise ConfigError("No name found")
        if type(name) != str:
            raise ConfigError("Name must be a string")
        return name
    
    def get_device_names(self) -> List[str]:
        device_list = self.config.get("devices")
        if not device_list:
            raise ConfigError("No Device List Found")
        if type(device_list) != list:
            raise ConfigError("Device List must be a list")
        return device_list

    def load_device_configs(self) -> List[dict]:
        devices = []
        for device_file in self.device_files:
            with open(f"config/devices/{device_file}", "r") as infile:
                devices.append(json.loads(infile.read()))
        return devices
    
    def load_device_managers(self) -> dict[str, BleakClient]:
        device_loader = DeviceLoader(self.device_configs)
        return device_loader.get_devices()
    
    def save_device(self, name, address):
        device_config = {"name" : name, "address" : address}
        file_name = format_config_name(name)
        path = f"config/devices/{file_name}.config"
        if os.path.isfile(path):
            print(f"Device called {name} already exists!")
            return
        with open(path, "w") as outfile:
            outfile.write(json.dumps(device_config))
        

if __name__=="__main__":
    loader = ConfigLoader("new_config.config")
    print(loader.get_config_name())
    print(loader.get_device_names())
    print(loader.device_files)
    print(loader.load_device_configs())
    print(loader.load_device_managers())