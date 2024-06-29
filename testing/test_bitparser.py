from src.helpers import get_format_string, parse_bytearray
def test_char():
    lengths = [1]
    signeds = [True]
    assert get_format_string(lengths, signeds) == "b"

def test_unsigned_char():
    lengths = [1]
    signeds = [False]
    assert get_format_string(lengths, signeds) == "B"

def test_multiple_chars():
    lengths = [1, 1]
    signeds = [True, True]
    assert get_format_string(lengths, signeds) == "bb"

def test_different_signs():
    lengths = [1,1]
    signeds = [True, False]
    assert get_format_string(lengths, signeds) == "bB"

def test_different_lengths():
    lengths = [1, 2]
    signeds = [True, True]
    assert get_format_string(lengths, signeds) == "bh"
    
def test_different_lengths_and_signs():
    lengths = [1, 2]
    signeds = [True, False]
    assert get_format_string(lengths, signeds) == "bH"

# === Parser ===
def test_single_value():
    config = {"chunks": [{"length": 4, "remainder": 16, "signed": True}]}
    data = bytearray(b'\x85X\x06\x01')
    assert parse_bytearray(config, data) == [262.3457794189453]
