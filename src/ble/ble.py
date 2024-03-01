import asyncio
from bleak import BleakScanner, BleakClient

address = "6F:8E:81:C0:9A:40" # my phones address
GENERIC_ACCESS = "1800"
UART_ACCESS_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
CHARACTERISTIC_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

async def main(address):
    async with BleakClient(address) as client:
        services = client.services
        print(f"Services: {list(services)}")

asyncio.run(main(address))