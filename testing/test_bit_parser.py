from typing import Any
import pytest

from src.ble.bit_parser import BitParser

@pytest.fixture
def parser_config() -> dict[str, Any]:
    return {
        "name" : "Raw Data",
        "num_values" : 2,
        "total_bytes" : 4,
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
        ]
    }

@pytest.fixture
def bit_parser(parser_config):
    return BitParser(parser_config)

def test_encode_bits_success(bit_parser):
    # x = 10, y = 5
    # x_Q = 10240, y_Q = 5120
    # x_B = 0010100000000000, y_B = 0001010000000000
    # x_H = \x28\x00, y_H = \x14\x00
    # desired_result: bytes = b'00101000000000000001010000000000'
    desired_result: bytes = b'\x28\x00\x14\x00'
    assert bit_parser.parse_data([10, 5]) == desired_result

def test_encode_zero(bit_parser):
    assert bit_parser.parse_data([0, 0]) == b'\x00\x00\x00\x00'

def test_encode_bits_fail_too_many(bit_parser):
    with pytest.raises(ValueError):
        bit_parser.parse_data([1, 2, 3])

def test_encode_bits_fail_not_enough(bit_parser):
    with pytest.raises(ValueError):
        bit_parser.parse_data([1])

def test_decode_bits_success(bit_parser):
    desired_result = [10, 5]
    assert bit_parser.parse_bits(b'\x28\x00\x14\x00') == desired_result

def test_decode_zero(bit_parser):
    assert bit_parser.parse_bits(b'\x00\x00\x00\x00') == [0, 0]

def test_decode_bits_fail_too_long(bit_parser):
    with pytest.raises(ValueError):
        bit_parser.parse_bits(b'\x00\x01')

def test_decode_bits_fail_too_short(bit_parser):
    with pytest.raises(ValueError):
        bit_parser.parse_bits(b'\x28\x00\x14\x00\x02\x04')

def test_Q_encoding(bit_parser):
    encoding = "6Q10"
    assert bit_parser.Q_encode(10, encoding) == 10240

def test_Q_decoding(bit_parser):
    encoding = "6Q10"
    assert bit_parser.Q_decode(10240, encoding) == 10
