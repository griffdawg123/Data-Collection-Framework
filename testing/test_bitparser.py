from src.helpers import get_format_string, parse_bytearray
def test_char():
    lengths = [1]
    signeds = [True]
    types = ["fixed"]
    assert get_format_string(lengths, signeds, types) == "b"

def test_unsigned_char():
    lengths = [1]
    signeds = [False]
    types = ["fixed"]
    assert get_format_string(lengths, signeds, types) == "B"

def test_multiple_chars():
    lengths = [1, 1]
    signeds = [True, True]
    types = ["fixed", "fixed"]
    assert get_format_string(lengths, signeds, types) == "bb"

def test_different_signs():
    lengths = [1,1]
    signeds = [True, False]
    types = ["fixed", "fixed"]
    assert get_format_string(lengths, signeds, types) == "bB"

def test_different_lengths():
    lengths = [1, 2]
    signeds = [True, True]
    types = ["fixed", "fixed"]
    assert get_format_string(lengths, signeds, types) == "bh"
    
def test_different_lengths_and_signs():
    lengths = [1, 2]
    signeds = [True, False]
    types = ["fixed", "fixed"]
    assert get_format_string(lengths, signeds, types) == "bH"

# === Parser ===
def test_single_value():
    config = {"chunks": [{"length": 4, "remainder": 16, "signed": True, "type": "fixed"}]}
    data = bytearray(b'\x85X\x06\x01')
    assert parse_bytearray(config, data) == [ 262.3457794189453 ]
