from typing import Any
import pytest

from src.ble.bit_parser import BitParser

@pytest.fixture
def parser_config() -> dict[str, Any]:
    return {
        "name" : "Raw Data",
        "num_values" : 9,
        "total_bytes" : 18,
        "services" : [
            {
                "name" : "accel_x",
                "data_type" : "int16",
                "num_bytes" : 2,
                "encoding" : "6Q10",
                "units" : "G"
            },
            {
                "name" : "accel_y",
                "data_type" : "int16",
                "num_bytes" : 2,
                "encoding" : "6Q10",
                "units" : "G"
            },
            {
                "name" : "accel_z",
                "data_type" : "int16",
                "num_bytes" : 2,
                "encoding" : "6Q10",
                "units" : "G"
            },
            {
                "name" : "gyro_x",
                "data_type" : "int16",
                "num_bytes" : 2,
                "encoding" : "11Q5",
                "units" : "deg/s"
            },
            {
                "name" : "gyro_y",
                "data_type" : "int16",
                "num_bytes" : 2,
                "encoding" : "11Q5",
                "units" : "deg/s"
            },
            {
                "name" : "gyro_z",
                "data_type" : "int16",
                "num_bytes" : 2,
                "encoding" : "11Q5",
                "units" : "deg/s"
            },
            {
                "name" : "comp_x",
                "data_type" : "int16",
                "num_bytes" : 2,
                "encoding" : "12Q4",
                "units" : "micT"
            },
            {
                "name" : "comp_y",
                "data_type" : "int16",
                "num_bytes" : 2,
                "encoding" : "12Q4",
                "units" : "micT"
            },
            {
                "name" : "comp_z",
                "data_type" : "int16",
                "num_bytes" : 2,
                "encoding" : "12Q4",
                "units" : "micT"
            },
        ]
    }

@pytest.fixture
def bit_parser(parser_config):
    return BitParser(parser_config)

def test_encode_bits_success():
    pass

def test_encode_bits_fail():
    pass

def test_decode_bits_success():
    pass

def test_decode_bits_fail():
    pass