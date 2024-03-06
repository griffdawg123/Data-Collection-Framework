# https://anandology.com/blog/using-iterators-and-generators/
from typing import Generator, Any, Iterator
import threading

class thread_safe:
    def __init__(self, gen: Generator[Any, None, None]) -> None:
        self.gen: Generator[Any, None, None] = gen
        self.lock = threading.Lock()
    
    def __iter__(self):
        return self
    
    def next(self):
        with self.lock:
            return next(self.gen, None)