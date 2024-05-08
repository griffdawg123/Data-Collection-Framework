import json
from typing import List, Dict, Optional
import os

from bleak import BleakClient

from src.loaders.config_error import ConfigError
from src.loaders.device_loader import DeviceLoader
from src.helpers import format_config_name

class ConfigLoader():
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.config = self.load_config()
    # load configuration for workspace
    def load_config(self) -> Dict:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config Path: {self.config_path} does not exist")

        with open(self.config_path, "r") as infile:
            return json.loads(infile.read())


    # save edited configuration at the end of a session
    def save_config(self, config_dict) -> None:
        self.config = config_dict
        with open(self.config_path, "w") as outfile:
            outfile.write(json.dumps(config_dict))

    # load bleak clients defined by initial config file
    def load_devices(self) -> Dict[str, BleakClient]:
        devices = self.config.get("devices")
        if type(devices) != list:
            raise ValueError("Config devices is not a list")
        device_dict = {} 
        for device_file_name in devices:
            with open(f"config/devices/{format_config_name(device_file_name)}.config", "r") as infile:
                device_conf = json.loads(infile.read())
                device_dict[device_conf["name"]] = BleakClient(device_conf["address"]) 
        return device_dict 

    # save a device file when it is added to a workspace
    def save_device(self, device_dict: Dict["str", "str"]) -> None:
        file_name = format_config_name(device_dict["name"])
        with open(f"config/devices/{file_name}", "w") as outfile:
            outfile.write(json.dumps(device_dict)) 
# class ConfigLoader():
#     def __init__(self, config_path: str) -> None:
#         # print(config_path)
#         self.config_path = config_path
#         self.config = self.load_config()
#         self.device_files = [f"{conf}.config" for conf in self.get_device_names()]
#         self.device_configs = self.load_device_configs()

#     def load_config(self):
#         with open(self.config_path, "r") as infile:
#             return json.loads(infile.read())
        
#     def save_config(self):
#         with open(self.config_path, "w") as outfile:
#             outfile.write(json.dumps(self.config))

#     def get_config_name(self) -> str:
#         name = self.config.get("name")
#         if not name:
#             raise ConfigError("No name found")
#         if type(name) != str:
#             raise ConfigError("Name must be a string")
#         return name
    
#     def get_device_names(self) -> List[str]:
#         device_list = self.config.get("devices")
#         if device_list is None:
#             raise ConfigError("No Device List Found")
#         if type(device_list) != list:
#             raise ConfigError("Device List must be a list")
#         return device_list

#     def load_device_configs(self) -> List[dict]:
#         devices = []
#         for device_file in self.device_files:
#             # print(device_file)
#             # device_file_obj = json.loads(device_file)
#             with open(f"config/devices/{device_file}", "r") as infile:
#                 # print(infile.read())
#                 data = infile.read()
#                 print(data)
#                 devices.append(json.loads(data))
#         return devices
    
#     def load_device_managers(self) -> dict[str, BleakClient]:
#         print("device configs: ", self.device_configs)
#         device_loader = DeviceLoader(self.device_configs)
#         return device_loader.get_devices()
    
#     def save_device(self, name, address):
#         device_config = {"name" : name, "address" : address}
#         file_name = format_config_name(name)
#         path = f"config/devices/{file_name}.config"
#         if os.path.isfile(path):
#             print(f"Device called {name} already exists!")
#             return
#         with open(path, "w") as outfile:
#             outfile.write(json.dumps(device_config))
#         device_list = self.config["devices"]
#         if device_list is not None:
#             device_list = list(device_list)
#             device_list.append(file_name)
#             self.config["devices"] = device_list
#         self.device_configs.append(device_config)
#         self.save_config()

#     def load_device(self, device_path):
#         device_list = self.config["devices"]
#         if device_list is not None:
#             device_list = list(device_list)
#             device_list.append(device_path.split("/")[-1].split(".")[0])
#             self.config["devices"] = device_list
#         self.device_configs = self.load_device_configs()
#         print(self.device_configs)
#         self.save_config()
    
#     def remove_device(self, device_name):
#         device_list = self.config["devices"]
#         if device_list is not None:
#             device_list=list(device_list)
#             print(device_list)
#             device_list.remove(format_config_name(device_name))
#             self.config["devices"] = device_list
#         self.device_configs = list(filter(lambda config: config["name"] != device_name, self.device_configs))
#         self.save_config()
        

# if __name__=="__main__":
#     loader = ConfigLoader("config/workspaces/new_config.config")
#     loader.save_device("Helo", "world")
#     print(loader.device_configs)