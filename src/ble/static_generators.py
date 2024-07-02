import math

from typing import Callable


def source_coro(next_coro, index = 0):
    try:
        while True:
            data = yield
            print(f"Source received: {data}")
            next_coro.send(data[index])
    except GeneratorExit:
        print("Exiting Coro")

def func_coro(func, next_coro):
    try:
        while True:
            data = yield
            print(f"Func received: {data}")
            print(f"func(data) = {func(data)}")
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

