import asyncio
import time
from typing import List, Tuple
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

async def scan_for_devices(future: asyncio.Future) -> None:
    devices = await BleakScanner.discover(return_adv=True)
    # print(devices)
    # All BLE devices must implement local name
    future.set_result([(x, y) for x, y in devices.values() if y.local_name])

def print_device_info(future: asyncio.Future):
    for device in future.result():
        d, a = device
        print(f"{d.name}: {d.address}")

if __name__ == "__main__":
    devices = []
    event_loop = asyncio.new_event_loop()
    future = asyncio.Future(loop = event_loop)
    future.add_done_callback(print_device_info)
    coro = scan_for_devices(future)
    event_loop.run_until_complete(coro)
    event_loop.close()
