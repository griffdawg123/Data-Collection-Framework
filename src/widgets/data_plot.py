import functools
import math
import time
from typing import Dict, Optional
from PyQt6.QtCore import QTimer, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
from bleak import BleakClient
from queue import Queue
import pyqtgraph as pg
import os
import sys
from qasync import QEventLoop
import asyncio

from src.ble.static_generators import coro, get_coro
from src.ble.threads import DataThread
from src.ble.ble_generators import NotifyThread
from src.helpers import hex_to_rgb

'''
plots : [
    {
        plot_name: "name",
        sources : [
            {
                device_name: "Thingy"
                service_name: "Battery Service"
                pen_color: "FFFF00"
                encoding:  [
                    {
                        "length" : 32,
                        "signed" : true,
                        "remainder": 16,
                        }
                    ]
                },
                data_points: [0],
            ],
        data_rate: 60,
        num_data_points: 100,
        y_max: 100,
        y_min: 0,
        x_label: "Time"
        y_label: "m/s"
    },
]
'''
class TrayItem(QWidget):
        
    delete_me = pyqtSignal(QWidget)

    def __init__(self, config: Dict, devices: Dict) -> None:
        super().__init__()
        self.config = config
        self.devices = devices

        self.remove_button = QPushButton("Remove Plot")
        self.edit_config_button = QPushButton("Edit Config")

        self.remove_button.clicked.connect(functools.partial(self.delete_me.emit, self))
        self.edit_config_button.clicked.connect(self.edit_config)

        self.plot = DataPlot()
        self.init_UI()

    def init_UI(self):
        buttons = QWidget()
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.edit_config_button)
        buttons.setLayout(button_layout)

        widget_layout = QHBoxLayout()
        widget_layout.addWidget(self.plot)
        widget_layout.addWidget(buttons)
        self.setLayout(widget_layout)

    def edit_config(self):
        print("unimplemented")

    def set_clients(self, clients):
        self.devices = clients

    def add_client(self, name, client):
        self.devices[name] = client

    def remove_client(self, name):
        del self.devices[name]

class Plots(pg.GraphicsLayoutWidget):
    def __init__(self, config, clients):
        super().__init__(show=True, title=config.get("title", ""))
        self.config = config
        self.clients = clients
        self.data = []
        self.init_rows(config.get("rows", []))
    
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
            self.init_sources(plot.get("sources", []), num_data_points, i, j)

    def init_sources(self, sources, datapoints, i, j):
        for k, source in enumerate(sources):
            # need to create a coroutine for source (BLE Notify, BLE Read and Time)
            # need to create a coroutine for function (Sin, Cos, Parsing, Identity, etc)
            # need to create a couroutine for updating 
            # ith row, jth plot, kth source
            queue = Queue(maxsize=datapoints)
            [ queue.put(0) for _ in range(datapoints) ]
            sink = get_coro(functools.partial(self.update_data, i, j, k))
            sink.__next__()
            func = get_coro(source.get("func").get("name"), sink, source.get("func").get("params"))
            func.__next__()
            source = get_coro(source.get("type"), func)
            source.__next__()
            
            source_info = {
                "data" : queue,
                "sink" : sink,
                "func" : func,
                "source" : source,
            }
            self.data[i][j].append(source_info)

    def update_data(self, i, j, k, data):
        # update then queue of this data
        print("Updating with", data)
        queue: Queue = self.data[i][j][k].get("data")
        queue.get()
        queue.put(data)

        
if __name__ == "__main__":
    config = {
    "title" : "Sin Plot",
    "rows" : [
      [
        {
            "sources" : [
                {

                    "type" : "time",
                    "func" : {
                        "name" : "sin",
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
    app = QApplication(sys.argv)
    plots = Plots(config, {})
    app.exec()



# class DataPlot(pg.PlotWidget):

#     frame_changed = pyqtSignal(int)

#     """
#     interval : 60 ms secs / frame
#     framerate : # frames / sec
#     """

#     def __init__(self, source: Optional[DataThread] = None, datarate: int = 60, num_data_points: int = 100, y_max: int = 10, y_min: int = 10):
#         super().__init__()
#         self.counter = 0
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.on_timeout)
#         self.time_last = time.time()
#         self.source = source
#         self.set_params(datarate, num_data_points, y_max, y_min)

#     def set_params(self, datarate: int = 60, num_data_points: int = 100, y_max: int = 10, y_min: int = 10):
#         print(f"setting params {datarate, num_data_points, y_max, y_min}")
#         self.timer.setInterval(int(1000/datarate))
#         self.data = Queue(maxsize=num_data_points)
#         self.num_data_points = num_data_points
#         [self.data.put(0) for _ in range(self.num_data_points)]
#         self.y_max = y_max
#         self.y_min = y_min
#         self.setup_UI()

#     def set_source(self, source: DataThread):
#         self.source = source
#         self.thread = QThread()
#         self.source.moveToThread(self.thread)
#         self.thread.start()
#         self.frame_changed.connect(self.source.get_value)
#         self.source.value.connect(self.generate_data)

#     def on_timeout(self):
#         self.counter += 1
#         self.frame_changed.emit(self.counter)
    
#     # invoke externally
#     def start(self):
#         print("Starting in data plot")
#         self.counter = 0
#         self.last_frames = 0
#         self.timer.start()

#     def stop(self):
#         self.timer.stop()

#     def setup_UI(self):
#         print("Setup UI")
#         pg.setConfigOption('background', 0.95)
#         self.setYRange(self.y_min, self.y_max)
#         self.plots = []
#         p_item = self.getPlotItem()
#         if p_item is not None:
#             self.plot = p_item.plot([], [], pen=pg.mkPen("r", width=2))
#         # self.frame_changed.connect(self.frame_rate)

#     '''
#     Currently, on timeout:
#         We increase counter and emit the counter value to the source 
#         The source will then emit the value it currently has which will then 
#         be added to the queue to be displayed in the graph
#     '''
#     @pyqtSlot(float)
#     def generate_data(self, i):
#         self.data.get()
#         self.data.put(i)
#         self.plot_data(range(len(self.data.queue)), self.data.queue)            

#     def plot_data(self, spaces, data):
#         self.plot.setData(spaces, data)

#     @pyqtSlot()
#     def restart(self):
#         self.data = Queue()
#         [self.data.put(0) for _ in range(self.num_data_points)]

#     @pyqtSlot(int)
#     def frame_rate(self, frames):
#         if time.time() - self.time_last > 1:
#             print(f"{self.source} FPS: {frames - self.last_frames}")
#             self.last_frames = frames
#             self.time_last = time.time()

#     def cleanup(self):
#         print("cleanup")
#         self.source.cleanup()

#     def send_value(self, value: bytes):
#         self.source.send_value(value)

# if __name__ == "__main__":
#     config = {
#             "plot_name": "name",
#             "sources" : [
#                 {
#                     "type" : "BLE",
#                     "device_name": "Thingy",
#                     "service_name": "Battery Service",
#                     "pen_color": "FFFF00",
#                     "encoding":  [
#                         {
#                             "length" : 32,
#                             "signed" : True,
#                             "remainder": 16,
#                             },
#                         ],
#                     "data_points": [0],
#                     },
#                 ],
#             "data_rate": 60,
#             "num_data_points": 100,
#             "y_max": 1,
#             "y_min": -1,
#             "x_label": "time",
#             "x_units": "s",
#             "y_label": "speed",
#             "y_units": "m/s",
#             }
#     source = config["sources"][0]
#     app = QApplication(sys.argv)
#     win = pg.GraphicsLayoutWidget(show = True, title = "Config based plots")

#     sin_plot = win.addPlot(title="Sin Graph")
#     sin_curve = sin_plot.plot(pen='y')
#     sin_plot.setLabel('left', config.get("y_label", ""), units=config.get("y_units", ""))
#     sin_plot.setLabel('bottom', config.get("x_label", ""), units=config.get("x_units", ""))
#     sin_plot.enableAutoRange('y', False)
#     sin_plot.setRange(yRange=(config["y_min"], config["y_max"]))
#     sin_data = Queue(maxsize=config.get("num_data_points", 100))
#     [sin_data.put(0) for _ in range(config.get("num_data_points", 100))]
#     sin_curve.setData(sin_data.queue)
     
#     win.nextRow()

#     cos_plot = win.addPlot(title="Cos Graph")
#     cos_curve = cos_plot.plot(pen='y')
#     cos_plot.setLabel('left', config.get("y_label", ""), units=config.get("y_units", ""))
#     cos_plot.setLabel('bottom', config.get("x_label", ""), units=config.get("x_units", ""))
#     cos_plot.enableAutoRange('y', False)
#     cos_plot.setRange(yRange=(config["y_min"], config["y_max"]))
#     cos_data = Queue(maxsize=config.get("num_data_points", 100))
#     [cos_data.put(0) for _ in range(config.get("num_data_points", 100))]
#     cos_curve.setData(cos_data.queue)


#     def update_data(queue, val):
#         queue.get()
#         queue.put(val)

#     def update_plot():
#         global sin_curve, cos_curve, data, time_last
#         sin_curve.setData(sin_data.queue)
#         cos_curve.setData(cos_data.queue)
#         time_last = time.time()

#     def sin_func(a, b, c, d, data):
#         return (a*math.sin(b*data+c)+d)
#     def cos_func(a, b, c, d, data):
#         return (a*math.cos(b*data+c)+d)

#     sin_sink = coro(functools.partial(update_data, sin_data))
#     sin_sink.__next__()
#     sin_source = coro(functools.partial(sin_func, 1, 1, 0, 0), sin_sink)
#     sin_source.__next__()
#     sin_get_time = coro(time.time, sin_source)
#     sin_get_time.__next__()

#     cos_sink = coro(functools.partial(update_data, cos_data))
#     cos_sink.__next__()
#     cos_source = coro(functools.partial(cos_func, 1, 1, 0, 0), cos_sink)
#     cos_source.__next__()
#     cos_get_time = coro(time.time, cos_source)
#     cos_get_time.__next__()

#     timer = QTimer()
#     timer.setInterval(int(1000/60))
#     timer.timeout.connect(functools.partial(sin_get_time.send, None))
#     timer.timeout.connect(functools.partial(cos_get_time.send, None))
#     timer.timeout.connect(update_plot)
#     timer.start()
#     app.exec()

