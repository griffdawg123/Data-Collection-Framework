import struct
from math import log
from typing import Dict, List, Optional
from PyQt6.QtWidgets import QWidget
from os import walk
import numpy as np
from operator import itemgetter

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


def to_value(format_string: str, remainder_array: List[int], data: bytearray) -> List[float]:
    assert len(format_string) == len(remainder_array)
    res = []
    for i, val in enumerate(struct.unpack(format_string, data)):
         res.append(val/(2**remainder_array[i]))
    return res

def get_format_string(lengths, signeds, types):
    FORMATS = {
        1 : "b",
        2 : "h",
        4 : "i",
        8 : "q",
            }
    assert len(lengths) == len(signeds)
    return "".join(["f" if types[i] == "float" else (FORMATS[lengths[i]] if signeds[i] else FORMATS[lengths[i]].upper()) for i in range(len(lengths))])

def parse_bytearray(chunks_config: Optional[Dict], bytes: bytearray) -> List[float]:
    chunks = chunks_config["chunks"] if chunks_config else [{"type": "float","length": len(bytes), "signed": True, "remainder":0}]
    if not bytes: return [0]
    total_len = len(bytes)
    print(total_len, chunks)
    lengths = [chunk["length"] for chunk in chunks]
    signeds = [chunk["signed"] for chunk in chunks]
    remainders = [chunk["remainder"] for chunk in chunks]
    types = [chunk["type"] for chunk in chunks]
    
    return to_value(get_format_string(lengths, signeds, types), remainders, bytes)

def hex_to_rgb(hex):
    if hex == "":
        hex = "FFFFFF"
    hex = hex.lstrip("#")
    assert len(hex) == 6
    return tuple([int(hex[i:i+2], 16) for i in range(0, 6, 2)])

if __name__ == "__main__":
    print(hex_to_rgb("#FFFFFF"))
