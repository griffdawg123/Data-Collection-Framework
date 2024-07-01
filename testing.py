# -*- coding: utf-8 -*-
"""
Notifications
-------------

Example showing how to add notifications to a characteristic and handle the responses.

Updated on 2019-07-03 by hbldh <henrik.blidh@gmail.com>

"""

import sys
import asyncio
import struct


from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from src.helpers import parse_bytearray, to_value

# def to_value(data: bytearray, format_string: str):
#     return struct.unpack(format_string, data) 

def notification_handler(characteristic: BleakGATTCharacteristic, data: bytearray):
    """Simple notification handler which prints the data received."""
    print(characteristic.description, data, to_value('i', [16], data))


async def main():
    print("Main started")
    async with BleakClient("F1:EC:95:17:0A:62") as client:

        print("Connected")

        await client.start_notify("ef680409-9b35-4933-9b10-52ffa9740042", notification_handler)
        await asyncio.sleep(5.0)
        await client.stop_notify("ef680409-9b35-4933-9b10-52ffa9740042")
    print("Main Finished")


if __name__ == "__main__":
    asyncio.run(main())
