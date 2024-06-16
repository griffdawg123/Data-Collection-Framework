from math import log
from typing import List, Optional
from PyQt6.QtWidgets import QWidget
from os import walk
import numpy as np

def center(window: QWidget) -> None:
    """takes a QWidget and centres it in the screen

    Args:
        window (QWidget): The window to be centred
    """
    screen_rect = window.frameGeometry()
    screen = window.screen()
    if screen is not None:
        screen_geometry = screen.availableGeometry()
        centre_point = screen_geometry.center()
        screen_rect.moveCenter(centre_point)
        window.move(screen_rect.topLeft())

def format_config_name(string: str) -> str:
    """Generates a config name by lower casing and joining a string with '_'

    Args:
        string (str): string to be converted to the config name

    Returns:
        str: the corresponding config name
    """
    return "_".join(string.lower().split())


def get_files(dir: str) -> list[str]:
    return next(walk(dir), (None, None, []))[2]

def parse_bytearray(bytes: bytearray, chunks: Optional[List] = None) -> List[float]:
    # need to be able to check for variable number of chunks of various encoding and lengths
    # tuples - length and remainder bits
    # (len (in bits), sign, remainders (in bits))
    if not chunks: chunks = [(len(bytes)*8, True, 0)]
    total_len = len(bytes)
    assert total_len*8 == sum([c[0] for c in chunks])
    # if m and n: assert log(m+n, 2) == num_bytes
    res = []
    for l, sign, rem in chunks:
        assert log(l, 2).is_integer()
        signed_flag = "i" if sign else "u"
        dt = np.dtype(f"{signed_flag}{int(l/8)}")
        val = float(np.frombuffer(bytes, dtype=dt))/(2**rem)
        res.append(val)
    return res

def hex_to_rgb(hex):
    if hex == "":
        hex = "FFFFFF"
    hex = hex.lstrip("#")
    assert len(hex) == 6
    return tuple([int(hex[i:i+2], 16) for i in range(0, 6, 2)])

if __name__ == "__main__":
    print(hex_to_rgb("#FFFFFF"))
