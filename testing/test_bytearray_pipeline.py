
import functools
import pytest

from src.ble.static_generators import func_coro, sink_coro, source_coro
from src.helpers import parse_bytearray

@pytest.fixture
def result_list():
    return []

@pytest.fixture
def sink(result_list):
    _sink = sink_coro(lambda val: result_list.append(val))
    next(_sink)
    return _sink

@pytest.fixture
def bytearray_config():
    return {"chunks" :[{
    "length": 32,
    "remainder": 16,
    "signed": False,
            }]}

@pytest.fixture
def func(sink, bytearray_config):
    _func = func_coro(functools.partial(parse_bytearray, bytearray_config) , sink)
    next(_func)
    return _func

@pytest.fixture
def source(func):
    _source = source_coro(True, func)
    next(_source)
    return _source

def test_byteparser():
    res = parse_bytearray(None, bytearray(b',|F\x00'))
    print(res)
    assert res

def test_three_bytes(source, result_list):
    values = [bytearray(b',|F\x00')]*3
    source.send(values[0])
    for _ in values:
        next(source)
    assert(result_list)

