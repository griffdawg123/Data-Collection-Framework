import functools
import time
import math

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

def get_coro(type, next_coro=None, args = {}):
    match type:
        case "time":
            return coro(time.time, next_coro)
        case "sin":
            print("sin")
            return coro(functools.partial(param_sin, args), next_coro)
        case "cos":
            return coro(functools.partial(param_cos, args), next_coro)
        case _:
            return coro(lambda x: x, next_coro)

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
    print(args)
    return a*math.sin(b*data + c)+d

