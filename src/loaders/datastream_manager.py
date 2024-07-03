from time import time
from typing import List, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from src.helpers import parse_bytearray
from src.loaders.singleton import Singleton
from bleak.backends.characteristic import BleakGATTCharacteristic

class DatastreamSignal(QObject):
    value_signal = pyqtSignal(str, list)

class DatastreamManager(metaclass=Singleton):
    def __init__(self) -> None:
        self.datastream_manager = DatastreamSignal()
        self.values = {}
        self.UUID_map = {}

    # When we receive the update signal, emit current value for each source currently loaded
    def source_update(self):
        for source, value in self.values.items():
            self.datastream_manager.value_signal.emit(source, value)
        self.datastream_manager.value_signal.emit("time", (time(),))

    def connect_to_signal(self, func):
        self.datastream_manager.value_signal.connect(func)

    def set_maps(self, UUID_map):
        self.UUID_map = UUID_map

    def update_value(self, characteristic: BleakGATTCharacteristic, data: bytearray):
        self.values[self.UUID_map[characteristic.uuid]["name"]] = parse_bytearray(
            self.UUID_map[characteristic.uuid],
            data
                )


