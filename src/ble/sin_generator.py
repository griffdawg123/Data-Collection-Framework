import time
import math
from queue import Queue

def get_sin():
    while True:
        yield math.sin(time.time())

if __name__ == "__main__":
    for i in get_sin():
        print(i)