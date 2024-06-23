import asyncio
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
def source_coro(next_coro):
    started = False
    value = None
    try:
        while True:
            data = yield
            print("Yielded:", data)
            if started:
                if not data: # if 'next' --> Retrieve value
                    to_send = value if value else time.time()
                    print("Sending:", to_send)
                    next_coro.send(to_send)
                else: # if sent value --> Set value
                    value = data
            started = True
    except:
        print("Exiting Coro")

def func_coro(func, next_coro):
    try:
        while True:
            data = yield
            print(func)
            print("Func:", func(data))
            next_coro.send(func(data))
    except:
        print("Exiting Coro")


# Takes a function to sink data into
def sink_coro(func: Callable):
    try:
        while True:
            data = yield
            func(data)
    except:
        print("Exiting Coro")

def coro(func, next_coro=None):
    try:
        while True:
            data = yield
            if next_coro:
                if data:
                    next_coro.send(func(data))
                else:
                    next_coro.send(func())
            else:
                if data:
                    func(data)
                else:
                    func()
    except GeneratorExit:
        print("Exiting Coro")

# For a non BLE source, time.time is called upon timeout
# Perhaps for BLE, notify callback sends a value to the coroutine, graph is only
# updated upon timeout
def get_coro(type, next_coro=None, args = {}, clients: Dict[str, BleakClient] = {}):
    new_coro = coro(lambda x: x, next_coro)
    match type:
        case "time":
            return coro(time.time, next_coro)
        case "sin":
            print("sin")
            return coro(functools.partial(param_sin, args), next_coro)
        case "cos":
            return coro(functools.partial(param_cos, args), next_coro)
        case "ble":
            # Args contains the name of the ble device
            loop = asyncio.get_event_loop()
            print(clients)
            try:
                client: BleakClient = clients[args.get("name")]
                print(client)
            except KeyError:
                return new_coro
            
            if not client.is_connected:
                print("not connected")
                _ = loop.create_task(client.connect())

            
            notify_task = loop.create_task(
                    client.start_notify(args.get("UUID"), 
                    functools.partial(ble_unpack, next_coro))
            )
            notify_task.add_done_callback(lambda _: print("Notify Started"))
        case "fixed_point":
            return coro(functools.partial(parse_bytearray), next_coro)
        case _:
            print("returning blank coro")
            return new_coro

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
