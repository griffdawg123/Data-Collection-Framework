import json
import os
import pytest
# from pytest import fixture, raises
from src.loaders.config_loader import ConfigLoader
from bleak import BleakClient

TEST_CONFIG = {
        "name" : "test workspace",
        "devices" : ["test_device"]
} 

TEST_DEVICE = {
    "name" : "test device",
    "address" : "test address"
}


@pytest.fixture(scope="session", autouse=True)
def create_config(request):
    with open("testing/test.config", "w+") as outfile:
        outfile.write(json.dumps(TEST_CONFIG))
    with open("config/devices/test_device.config", "w+") as outfile:
        outfile.write(json.dumps(TEST_DEVICE))
    request.addfinalizer(remove_config) # type: ignore

def remove_config():
    os.remove("testing/test.config")
    os.remove("config/devices/test_device.config")

def test_config_fixture():
    assert os.path.isfile("testing/test.config")

def test_load_config_exists():
    confloader = ConfigLoader("testing/test.config")
    config = confloader.load_config()
    assert config == TEST_CONFIG

def test_load_config_not_exists():
    with pytest.raises(FileNotFoundError):
        ConfigLoader("doesnt/exist.config")

def test_load_devices():
    confloader = ConfigLoader("testing/test.config")
    devices = confloader.load_devices()
    assert list(devices.keys()) == [TEST_DEVICE.get("name")]
    clients = devices.values()
    clients = list(clients)
    client = clients[0]
    assert type(client) == BleakClient
    assert client.address == TEST_DEVICE.get("address")

def test_save_config():
    confloader = ConfigLoader("testing/test.config")
    config = confloader.load_config()
    devices = config.get("devices")
    assert type(devices) == list
    devices.append("new device")
    config["devices"] = devices
    confloader.save_config(config)
    new_config = confloader.load_config()

    exp_config = TEST_CONFIG
    exp_devices = exp_config.get("devices")
    assert type(exp_devices) == list
    exp_devices.append("new device")
    exp_config["devices"] = exp_devices

    assert new_config == exp_config