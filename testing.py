from bleak import BleakClient
import asyncio


async def main():
    async with BleakClient("F1:EC:95:17:0A:62") as client:
        if client.is_connected:
            for service in client.services:
                characteristics = service.characteristics
                for c in characteristics:
                    descriptors = c.descriptors
                    for d in descriptors:
                        print(d.uuid)
asyncio.run(main())
