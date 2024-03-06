import time
import math
from queue import Queue
import itertools
from typing import Generator
import random
import os
import sys

# append path directory to system path so other modules can be accessed
myDir = os.getcwd()
sys.path.append(myDir)
from pathlib import Path
path = Path(myDir)
a=str(path.parent.absolute())
sys.path.append(a)
from src.ble.threads import DataThread

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

if __name__ == "__main__":
    q = Queue()
    q.put(0)
    print(q.queue)
    q.put(next(get_sin()))
    print(q.queue)
    print(list(itertools.islice(q.queue, 1)))