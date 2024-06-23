from src.ble.static_generators import func_coro, source_coro, sink_coro


sink_source = sink_coro(print)
next(sink_source)
# sqr_source = func_coro(lambda x: x**2, sink_source)
# next(sqr_source)
time_source = source_coro(sink_source)
next(time_source)

for i in range(10):
    next(time_source)
