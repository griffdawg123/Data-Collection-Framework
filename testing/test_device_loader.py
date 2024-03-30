from bleak import BleakClient
import pytest
from src.loaders.config_error import ConfigError
from src.loaders.device_loader import DeviceLoader

@pytest.fixture
def device_config_1():
    return [{
        "name" : "Thingy",
        "address" : "F1:EC:95:17:0A:62"
    }]

@pytest.fixture
def device_loader_1(device_config_1):
    return DeviceLoader(device_config_1)

@pytest.fixture
def device_config_2():
    return [{
        "name" : "Thingy",
        "address" : "F1:EC:95:17:0A:62"
    },
    {
        "name" : "Thingy2",
        "address" : "F1:EC:95:17:0A:63"
    }
    ]

@pytest.fixture
def device_loader_2(device_config_2):
    return DeviceLoader(device_config_2)

@pytest.fixture
def bad_config():
    return [{"name" : "hello"}]

def test_load_device(device_loader_1, device_config_1):
    devices = device_loader_1.get_devices()
    assert len(devices) == 1
    device_params = device_config_1[0]
    assert device_params["name"] in devices.keys()
    device = devices[device_params["name"]]
    assert type(device) == BleakClient
    assert not device.is_connected

def test_load_multiple_devices(device_loader_2, device_config_2):
    devices = device_loader_2.get_devices()
    assert len(devices) == 2
    device_params_1 = device_config_2[0]
    device_params_2 = device_config_2[1]
    assert device_params_1["name"] in devices.keys()
    assert device_params_2["name"] in devices.keys()
    device1 = devices[device_params_1["name"]]
    device2 = devices[device_params_2["name"]]
    assert type(device1) == BleakClient
    assert type(device2) == BleakClient
    assert not device1.is_connected
    assert not device2.is_connected
    assert device1 != device2

def test_no_devices():
    device_loader = DeviceLoader({})
    devices = device_loader.get_devices()
    assert len(devices) == 0

def test_no_address(bad_config):
    device_loader = DeviceLoader(bad_config)
    with pytest.raises(ConfigError):
        device_loader.get_devices()