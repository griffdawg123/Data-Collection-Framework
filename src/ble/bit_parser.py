from typing import List, Any, NewType, Union, TypeVar
import numpy as np
from numpy.typing import NBitBase

#TODO replace with Fixed Point optional parser

T2 = TypeVar("T2", bound=NBitBase)

int_types = {
    "int16" : np.int16,
    "int32" : np.int32,
    "uint16" : np.uint16,
    "uint32" : np.uint32,
}

class BitParser():
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.num_values = config["num_values"]
        self.num_bytes = config["total_bytes"]
        self.name = config["name"]
        self.services = config["services"]

    def parse_bits(self, data: bytes):
        if len(data) > self.num_bytes:
            raise ValueError("Incoming data too long")
        elif len(data) < self.num_bytes:
            raise ValueError("Incoming data too short")
        
        result = []
        for s in self.services:
            value = int.from_bytes(data[:s["num_bytes"]], 'big')
            print(data[:s["num_bytes"]])
            result.append(self.Q_decode(value, s["encoding"]))
            data = data[s["num_bytes"]:]
        return result

    def parse_data(self, data: List[int]):
        if len(data) > self.num_values:
            raise ValueError("Data to encode is too long")
        elif len(data) < self.num_values:
            raise ValueError("Data to encode is too short")
        
        result = b''
        for s in self.services:
            to_encode = self.Q_encode(data.pop(0), s["encoding"])
            print(to_encode)
            result += to_encode.to_bytes(s["num_bytes"], "big")
        return result
    
    def Q_encode(self, num: float, encoding: str):
        _, decimal = encoding.split("Q")
        return (num*2**int(decimal))

    def Q_decode(self, num: int, encoding: str):
        _, decimal = encoding.split("Q")
        return float(num/2**int(decimal))

