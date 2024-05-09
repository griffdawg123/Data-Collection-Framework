"""Config Loader to load and save config files

    Raises:
        FileNotFoundError: Raised when config file does not exist
        ValueError: Raised when config file is malformed

"""
import json
from typing import Dict
import os
from bleak import BleakClient
from src.helpers import format_config_name

class ConfigLoader():
    """
    Reads and writes config files
    """
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.config = self.load_config()
    # load configuration for workspace
    def load_config(self) -> Dict:
        """
        Loads the config dictionary in the specified config path 

        Raises:
            FileNotFoundError: if path does not point to a valid config path, error is raised

        Returns:
            Dict: Contains setup parameters of workspace
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config Path: {self.config_path} does not exist")

        with open(self.config_path, "r", encoding='utf8') as infile:
            return json.loads(infile.read())


    # save edited configuration at the end of a session
    def save_config(self, config_dict: Dict) -> None:
        """Saves a config dict to the specified file

        Args:
            config_dict (dict): contains the config dictionary specifying the workspace
        """
        self.config = config_dict
        with open(self.config_path, "w", encoding='utf8') as outfile:
            outfile.write(json.dumps(config_dict))

    # load bleak clients defined by initial config file
    def load_devices(self) -> Dict[str, BleakClient]:
        """Loads the specified device files as a BLE client

        Raises:
            ValueError: if config file is malformed, where devices field does not contain a list

        Returns:
            Dict[str, BleakClient]: dictionary containing the BLE clients
        """
        devices = self.config.get("devices")
        if not isinstance(devices, list):
            raise ValueError("Config devices is not a list")
        device_dict = {}
        for device_file_name in devices:
            device_config_path = f"config/devices/{format_config_name(device_file_name)}.config"
            with open(device_config_path, "r", encoding="utf8") as infile:
                device_conf = json.loads(infile.read())
                device_dict[device_conf["name"]] = BleakClient(device_conf["address"])
        return device_dict

    # save a device file when it is added to a workspace
    def save_device(self, device_dict: Dict[str, str]) -> None:
        """saves a new device config to a config file

        Args:
            device_dict (Dict[str, str]): Device dict with name and address values
        """
        file_name = format_config_name(device_dict["name"])
        with open(f"config/devices/{file_name}", "w", encoding='utf-8') as outfile:
            outfile.write(json.dumps(device_dict))

    def get_title(self) -> str:
        return self.config["name"]