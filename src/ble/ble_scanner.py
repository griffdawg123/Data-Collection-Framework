import asyncio
import time
from typing import Dict, List, Tuple
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

async def scan_for_devices(future: asyncio.Future) -> None:
    devices = await BleakScanner.discover(return_adv=True)
    future.set_result([(x, y) for x, y in devices.values() if y.local_name])

def get_services(client: BleakClient) -> Dict:
    if not client:
        return {}
    characteristics = client.services.characteristics
    services = {}
    for _, c in characteristics.items():
        for property in c.properties:
            service_properties = services.get(property, {})
            service_properties[c.description] = c.uuid
            services[property] = service_properties

    return services

async def main():
    async with BleakClient("F1:EC:95:17:0A:62") as client:
        services = get_services(client)
        print(services["read"])
        print(services["write"])
        print(services["notify"])

if __name__ == "__main__":
    asyncio.run(main())


'''
{
    "read" : {
        description : uuid,
        }
}
'''
