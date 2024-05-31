import asyncio
from math import sin
from time import time, sleep
from bleak import BleakClient
from functools import partial
from fixedpoint import FixedPoint
import numpy as np

from src.helpers import parse_bytearray
# Generator coroutine
# Signal sent by plot (timeout) is received by source
# Source then sends out its last value received from a device (or current value if non BLE)
# update graph

ADDRESS = "F1:EC:95:17:0A:62"

HEADING = "0409"

def get_url(UUID: str) -> str:
    return f"EF68{UUID}-9B35-4933-9B10-52FFA9740042"

def sin_coro():
    print("Starting sin coroutine")
    try:
        while True:
            t = (yield)
            print(sin(t))
    except GeneratorExit:
        print("Closing Coroutine")

def BLE_coro():
    print("Starting ble coro")
    try:
        while True:
            sender, data = (yield)
            print(f"{sender}: {data}")
    except GeneratorExit:
        print("Generator Exit")

def callback(coro, sender, data: bytearray):
    # qformat = {'signed': True, 'm': 16, 'n': 16}
    # x = FixedPoint(0, **qformat)
    # x.from_str(f"0x{data.hex()}")
    # x.from_str(data.hex())
    
    coro.send((sender, parse_bytearray(data, [(32, True, 16)]))) 

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Device connected")
        coro = BLE_coro()
        coro.__next__()
        # await client.start_notify(get_url(HEADING), partial(callback, coro)) 
        await client.start_notify(get_url(HEADING), partial(callback, coro)) 
        sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
    # data = bytearray(b'\x92>d\x01')
    # q32format = {'signed': False, 'm': 32}
    # q16format = {'signed': False, 'm': 16, 'n': 16}
    # # x = FixedPoint(0, **q32format)  
    # # y = FixedPoint(0, **q16format)  

    # x = FixedPoint(0, **q32format)  
    # y = FixedPoint(0, **q16format)  
    # x.from_str(f"0x{data.hex()}")
    # y.from_str(f"0x{data.hex()}")
    # print(f"x: {float(x)}, fmt: {x.qformat}")
    # print(f"y: {float(y)}, fmt: {y.qformat}")
    # z = float(np.frombuffer(data, np.int32)[0]/(2**16))
    # print(f"z: {float(z)}")
    # print(parse_bytearray(data, [(32, True, 16)]))
