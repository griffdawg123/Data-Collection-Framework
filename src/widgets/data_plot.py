import functools
from typing import Optional
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from queue import Queue
import pyqtgraph as pg
import sys
import asyncio
from qasync import QEventLoop
from bleak import BleakClient

from src.ble.static_generators import func_coro, param_cos, param_sin, sink_coro, source_coro
from src.helpers import hex_to_rgb, parse_bytearray

class Plots(pg.GraphicsLayoutWidget):
    def __init__(self, config, clients):
        super().__init__(show=True, title=config.get("title", ""))
        self.funcs = {
            "sin" : param_sin,
            "cos" : param_cos,
            "fixed_point" : parse_bytearray,
        }
        self.config = config
        self.clients = clients
        self.data = []
        self.init_rows(config.get("rows", []))
        self.timer = QTimer()
        self.timer.setInterval(int(1000/config.get("data_rate", 60)))
        self.init_timers()
        # self.timer.start()
    
    def init_rows(self, plot_configs):
        for i, row in enumerate(plot_configs):
            self.data.append([])
            self.init_plots(row, i)
            self.nextRow()

    def init_plots(self, row, i):
        for j, plot in enumerate(row):
            self.data[i].append([])
            new_plot = self.addPlot(title=plot.get("title"))
            new_plot.setLabel('left', plot.get("y_label", ""), units=plot.get("y_units", ""))
            new_plot.setLabel('bottom', plot.get("x_label", ""), units=plot.get("x_units", ""))
            new_plot.enableAutoRange('y', False)
            new_plot.setRange(yRange=(plot.get("y_min", 0), plot.get("y_max", 100)))
            
            num_data_points = plot.get("num_data_points", 100)
            self.init_sources(new_plot, plot.get("sources", []), num_data_points, i, j)

    def init_sources(self, plot: pg.PlotItem, sources, datapoints, i, j):
        for k, source in enumerate(sources):
            # need to create a coroutine for source (BLE Notify, BLE Read and Time)
            # need to create a coroutine for function (Sin, Cos, Parsing, Identity, etc)
            # need to create a couroutine for updating 
            # ith row, jth plot, kth source
            queue = Queue(maxsize=datapoints)
            [ queue.put(0) for _ in range(datapoints) ]
            sink = sink_coro(functools.partial(self.update_data, i, j, k))
            next(sink)
            func = func_coro(
                    functools.partial(
                        self.funcs.get(source.get("func", {}).get("type"), lambda x: x),
                        source.get("func", {}).get("params", {})
                    ),
                    sink
                    )
            next(func)

            data_source = source_coro(func)
            next(data_source)

            client: Optional[BleakClient] = None
            if source.get("type", "") == "ble":
                args = source.get("args", {})
                client = self.clients.get(args.get("name", None), None)
                assert(client)
                loop = asyncio.get_event_loop()
                notify_task = loop.create_task(client.start_notify(args.get("UUID"), lambda _, data: data_source.send(data)))
                notify_task.add_done_callback(lambda _: print("notify started"))
                

            curve = plot.plot(pen=hex_to_rgb(source.get("pen_color", "FFFFFF")))
            curve.setData(queue.queue)
            
            source_info = {
                "data" : queue,
                "sink" : sink,
                "func" : func,
                "source" : data_source,
                "curve" : curve,
                "client" : client,
            }
            self.data[i][j].append(source_info)

    def update_data(self, i, j, k, data):
        # update then queue of this data
        print("Data: ", data)
        queue: Queue = self.data[i][j][k].get("data")
        queue.get()
        queue.put(data)

    def update_plots(self):
        # print("Updating plots")
        for row in self.data:
            for plot in row:
                for source in plot:
                    source["curve"].setData(source["data"].queue)

    def on_timeout(self, source):
        next(source)
        

    def init_timers(self):
        for row in self.data:
            for plot in row:
                for source in plot:
                    print("Plot")
                    self.timer.timeout.connect(functools.partial(self.on_timeout, source["source"]))
                    print("Sending to source", source)
        self.timer.timeout.connect(self.update_plots)


    def restart(self):
        for row in self.data:
            for plot in row:
                for source in plot:
                    datapoints = len(source["data"].queue)
                    queue = Queue(maxsize=datapoints)
                    [ queue.put(0) for _ in range(datapoints) ]
                    source["data"] = queue

    def stop(self):
        self.timer.stop()

    def start(self):
        print("start")
        self.timer.start()

if __name__ == "__main__":
    config = {
    "rows" : [
      [
        {
            "title" : "Sin Plot",
            "sources" : [
                {

                    "type" : "time",
                    "func" : {
                        "type" : "sin",
                        "params" : {
                            "a" : 1,
                            "b" : 1,
                            "c" : 0,
                            "d" : 0,
                        },
                    },
                    "pen_colour" : "FFFF00",
                    "source_name" : "sin"
                }
            ],
            "num_data_points" : 100,
            "y_max" : 1,
            "y_min" : -1,
            "x_label" : "Time",
            "x_units" : "s",
            "y_label" : "Value",
            "y_units" : ""
        }
      ]
    ],
    "data_rate" : 60
}


    # config = {
    # "rows" : [
    #   [
    #     {
    #         "title" : "BLE Plot",
    #         "sources" : [
    #             {
    #                 "type" : "ble",
    #                 "func" : {
    #                     "name" : "fixed_point",
    #                     "params" : {
    #                         "chunks" : [
    #                             {"length":32,"signed":False,"remainder":16}    
    #                         ]
    #                     },
    #                 },
    #                 "pen_colour" : "FFFF00",
    #                 "source_name" : "Heading",
    #                 "args" : {
    #                     "UUID":  "EF680409-9B35-4933-9B10-52FFA9740042",
    #                     "name": "Thingy",
    #                 },
    #             }
    #         ],
    #         "num_data_points" : 100,
    #         "y_max" : 360,
    #         "y_min" : 0,
    #         "x_label" : "Time",
    #         "x_units" : "s",
    #         "y_label" : "Heading",
    #         "y_units" : "Degrees"
    #     }
    #   ]
    # ],
    # "data_rate" : 60
# }

    app = QApplication(sys.argv)
    plots = Plots(config, {})
    plots.start()
    sys.exit(app.exec())
