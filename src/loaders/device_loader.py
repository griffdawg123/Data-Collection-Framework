from bleak import BleakClient
from typing import List
from src.loaders.config_error import ConfigError

class DeviceLoader():
    def __init__(self, config) -> None:
        self.config = config

    def get_devices(self) -> dict[str, BleakClient]:
        devices = {}
        for conf in self.config:
            name = ""
            address = ""
            try:
                name = conf["name"]
            except KeyError:
                raise ConfigError("Name field not found")
            
            try:
                address = conf["address"]
            except KeyError:
                raise ConfigError("Address field not found")
            devices[name] = BleakClient(address)
        return devices
    
