import asyncio
import time
from typing import Dict, List, Tuple
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

async def scan_for_devices(future: asyncio.Future) -> None:
    devices = await BleakScanner.discover(return_adv=True)
    future.set_result([(x, y) for x, y in devices.values() if y.local_name])

def get_services() -> Dict[str, str]:
    return {}

async def main():
    async with BleakClient("F1:EC:95:17:0A:62") as client:
        print(client.address)

if __name__ == "__main__":
    asyncio.run(main())
