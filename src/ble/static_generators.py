import asyncio
from collections import deque
import functools
import time
import math

from bleak import BleakClient
from typing import Callable, Coroutine, Dict, Generator

from src.helpers import parse_bytearray

# need to be able to update internal value until it needs to be updated
# send to value can happen whenever, when next is called, we pull the current value

# Takes a coroutine to pass data to

# Call next to update graph data, call send to update internal data
# Implement threadsafe queue
def source_coro(takes_input: bool, next_coro):
    started = False
    # values = deque(maxlen=5)
    value = None if takes_input else time.time()
    try:
        while True:
            data = yield
            print("Yielded:", data)
            if not data: # if 'next' --> Retrieve value
                print(f" Data!: {data}")
                # to_send = time.time()
                # if len(values) > 0:
                #     to_send = values.popleft()
                to_send = value if takes_input else time.time()
                if to_send:
                    print("Sending:", to_send)
                    next_coro.send(to_send)
            else: # if sent value --> Set value
                value = data
                # values.appendleft(data)
                # if len(values) > 2:
                #     values.pop()
    except GeneratorExit:
        print("Exiting Coro")

def func_coro(func, next_coro):
    try:
        while True:
            data = yield
            print(f"Received Data: {data}")
            print(func)
            print("Func:", func(data))
            next_coro.send(func(data))
    except GeneratorExit:
        print("Exiting Coro")


# Takes a function to sink data into
def sink_coro(func: Callable):
    try:
        while True:
            data = yield
            func(data)
    except GeneratorExit:
        print("Exiting Coro")

def param_cos(args, data):
    a = args["a"]
    b = args["b"]
    c = args["c"]
    d = args["d"]
    return a*math.cos(b*data + c)+d

def param_sin(args, data):
    a = args["a"]
    b = args["b"]
    c = args["c"]
    d = args["d"]
    return a*math.sin(b*data + c)+d

def ble_unpack(next_coro, _, data):
    print("unpacking")
    next_coro.send(data)

async def main():
    '''

    Replace source coroutine with a notify that sends to the next coroutine
    

    '''
    async with BleakClient("F1:EC:95:17:0A:62") as client:
        # await client.start_notify("EF680409-9B35-4933-9B10-52FFA9740042", print)

        def set_value(x):
            print("Setting data")
            print(x)

        sink = coro(set_value)
        sink.__next__()
        await client.start_notify("EF680409-9B35-4933-9B10-52FFA9740042", functools.partial(ble_unpack, sink))
        # loop = asyncio.get_event_loop()
        # notify_task = loop.create_task(
        #         client.start_notify(
        #             "EF680409-9B35-4933-9B10-52FFA9740042",
        #             print))
        # notify_task.add_done_callback(lambda _: print("Notify finished"))
        # args = {
        #         "name" : "thingy",
        #         "UUID" : "EF680409-9B35-4933-9B10-52FFA9740042"
        #         }
        # source = get_coro("ble", next_coro=sink, args=args, clients={"thingy": client})
        # source.__next__()
        time_now = time.time()
        while time.time() - time_now < 10:
            continue

        # await client.stop_notify("EF6804049-9B35-4933-9B10-52FFA9740042")
if __name__ == "__main__":
    # 
    asyncio.run(main())
