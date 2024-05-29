import functools
import time
import math
from queue import Queue
import itertools
from typing import Generator
import random
import os
import sys

from PyQt6.QtCore import QObject, pyqtSignal

from src.ble.threads import DataThread

def coro(func, next_coro=None):
    print("Starting coro")
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
            return coro(functools.partial(param_sin, args), next_coro)
        case _:
            return coro(lambda x: x, next_coro)

def param_sin(args, data):
    a = args["a"]
    b = args["b"]
    c = args["c"]
    d = args["d"]
    return a*math.sin(b*data + c)+d

def get_sin() -> Generator[float, None, None]:
    while True:
        time.sleep(0.05)
        yield math.sin(time.time())


class SinThread(DataThread):
    def __init__(self) -> None:
        super().__init__()
    
    def get_value(self):
        self.value.emit(math.sin(time.time()))

def get_random() -> Generator[float, None, None]:
    while True:
        time.sleep(0.1)
        yield random.random()

class RandomThread(DataThread):
    def __init__(self) -> None:
        super().__init__()
    
    def get_value(self):
        self.value.emit(random.random())

class ProducerCoro():

    def __init__(self, func, next_coro):
        super().__init__()
        self.func = func
        self.next_coro = next_coro
        self.routine = self.coro()
    
    def coro(self):
        print("Starting coro")
        try:
            while True:
                inbound = yield
                self.data.emit(self.func(inbound))
        except GeneratorExit:
            print("Closing coro")

    def start(self):
        self.routine.__next__()

    def send(self, data):
        self.routine.send(data)

    def result_func(self, func):
        self.data.connect(func)

def sin_coro(a, b, c, d):
    print("Starting Sin Coro")
    try:
        while True:
            data = yield
            print(f"{a}sin({b}x+{c})+{d} = {a*math.sin(b*data+c)+d}")
    except GeneratorExit:
        print("Closing Sin Coro")

if __name__ == "__main__":
    def sin_func(a, b, c, d, data):
        return (a*math.sin(b*data+c)+d)
    
    sink = coro(print)
    sink.__next__()
    source = coro(functools.partial(sin_func, 1, 1, 0, 0), sink)
    source.__next__()

    start_time = time.time()
    while time.time() - start_time < 100:
        source.send(time.time())
