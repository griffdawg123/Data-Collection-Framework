from typing import List, Any, NewType, Union
import numpy as np

class BitParser():
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    def parse_bits(self, data: bytes):
        pass

    def parse_data(self, data: List[np.unsignedinteger | np.signedinteger]):
        pass