import time
import math

from typing import Callable


def source_coro(takes_input: bool, next_coro):
    value = None if takes_input else time.time()
    try:
        while True:
            data = yield
            if not data: # if 'next' --> Retrieve value
                to_send = value if takes_input else time.time()
                if to_send:
                    next_coro.send(to_send)
            else: # if sent value --> Set value
                value = data
    except GeneratorExit:
        print("Exiting Coro")

def func_coro(func, next_coro):
    try:
        while True:
            data = yield
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

