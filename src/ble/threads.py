# https://anandology.com/blog/using-iterators-and-generators/
from typing import Generator, Any, Iterator
import threading
from PyQt6.QtCore import QThread, pyqtSignal, QRunnable

class DataThread(QThread):

    value = pyqtSignal(float)

    def __init__(self, gen: Generator[float, None, None]) -> None:
        super().__init__()
        self.gen: Generator[float, None, None] = gen

    def get_value(self):
        self.value.emit(next(self.gen))


    
