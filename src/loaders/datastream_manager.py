from time import time
from typing import List, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from src.loaders.singleton import Singleton

class DatastreamSignal(QObject):
    value_signal = pyqtSignal(str, tuple)

class DatastreamManager(metaclass=Singleton):
    def __init__(self) -> None:
        self.datastream_manager = DatastreamSignal()
        self.values = {}

    # When we receive the update signal, emit current value for each source currently loaded
    def source_update(self):
        for source, value in self.values:
            self.datastream_manager.value_signal.emit(source, value)
        self.datastream_manager.value_signal.emit("Time", (time(),))

    def connect_to_signal(self, func):
        self.datastream_manager.value_signal.connect(func)

