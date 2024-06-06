import asyncio
import functools
import time
import math

from bleak import BleakClient
from typing import Dict

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
            client: BleakClient = clients[args.get("name")]
            print(client)
            notify_task = loop.create_task(client.start_notify(args.get("UUID"), functools.partial(ble_unpack, next_coro)))
            notify_task.add_done_callback(lambda _: new_coro.__next__)
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
    async with BleakClient("F1:EC:95:17:0A:62") as client:
        await client.start_notify("EF680409-9B35-4933-9B10-52FFA9740042", print)

        # value = 0
        # def set_value(x):
        #     print("Setting data")
        #     global value
        #     value = x

        # sink = coro(set_value)
        # sink.__next__()
        # source = get_coro("ble", next_coro=sink, args={"name" : "thingy", "UUID" : "EF680409-9B35-4933-9B10-52FFA9740042"}, clients={"thingy": client})
        # source.__next__()
        time_now = time.time()
        while time.time() - time_now < 10:
            # print(value)
            continue

        await client.stop_notify("EF6804049-9B35-4933-9B10-52FFA9740042")
if __name__ == "__main__":
    asyncio.run(main())
