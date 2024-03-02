import time
import math
from queue import Queue
import itertools
from typing import Generator

def get_sin() -> Generator[float, None, None]:
    while True:
        yield math.sin(10*time.time())

if __name__ == "__main__":
    q = Queue()
    q.put(0)
    print(q.queue)
    q.put(next(get_sin()))
    print(q.queue)
    print(list(itertools.islice(q.queue, 1)))