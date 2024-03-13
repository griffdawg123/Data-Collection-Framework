import asyncio
from bleak import BleakClient
import numpy as np
from numpy import uint8

ADDRESS = "F1:EC:95:17:0A:62"
DEVICE_NAME = "0101"
BATTERY_LEVEL = "2a19"
# BATTERY_LEVEL = "180F"
HEADING = "0409"

def get_url(UUID: str) -> str:
    return f"EF68{UUID}-9B35-4933-9B10-52FFA9740042"

def dfu_url(UUID: str) -> str:
    return f"0000{UUID}-0000-1000-8000-00805f9b34fb"


async def read_name() -> None:
    async with BleakClient(ADDRESS) as client:
        print(f"Connected to {ADDRESS}: {client.is_connected}")
        try:
            device_name = await client.read_gatt_char(get_url(DEVICE_NAME))
            print("Device Name: {0}".format("".join(map(chr, device_name))))
        except Exception:
            pass
    return

async def write_name(name: str) -> None:
    async with BleakClient(ADDRESS) as client:
        print(f"Connected to {ADDRESS}: {client.is_connected}")
        try:
            await client.write_gatt_char(get_url(DEVICE_NAME), bytes(name, 'utf-8'))
        except Exception:
            pass
        print(f"Wrote name as {name} successfully")
    return

async def battery_level() -> None:
    async with BleakClient(ADDRESS) as client:
        print(f"Connected to {ADDRESS}: {client.is_connected}")
        try:
            battery_level = await client.read_gatt_char(dfu_url(BATTERY_LEVEL))
            print("Battery is at {0}%".format(np.frombuffer(battery_level, dtype=uint8)[0]))
        except Exception as e:
            print(e)



#data is sent as hex 
# if 16Qn, divide by 2**n
async def heading() -> None:
    async with BleakClient(ADDRESS) as client:
        print(f"Connected to {ADDRESS}: {client.is_connected}")
        await client.start_notify(get_url(HEADING), lambda char, data: print(float(np.frombuffer(data, np.int32)[0])/float(2**16)))
        await asyncio.sleep(5)
        await client.stop_notify(get_url(HEADING))

# async def 

    


if __name__=="__main__":
    # asyncio.run(read_name())
    # asyncio.run(write_name("Kaete"))
    # asyncio.run(read_name())
    # asyncio.run(battery_level())
    asyncio.run(heading())

