
from bleak import BleakClient
from src.loaders.device_manager import DeviceManager

def test_get_clients_before_change():
    ref1 = DeviceManager()
    ref2 = DeviceManager()
    assert(ref1 is ref2)
    client_name = "client"
    client = BleakClient("Address")
    ref1.add_client(client_name, client)
    assert(ref2.get_clients() == {client_name: client})

def test_get_clients_after_change():
    ref1 = DeviceManager()
    client_name = "client"
    client = BleakClient("Address")
    ref1.add_client(client_name, client)
    ref2 = DeviceManager()
    assert(ref1 is ref2)
    assert(ref2.get_clients() == {client_name: client})
