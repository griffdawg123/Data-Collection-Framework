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

from src.ble.static_generators import coro
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

class DataPlot(pg.PlotWidget):

    frame_changed = pyqtSignal(int)

    """
    interval : 60 ms secs / frame
    framerate : # frames / sec
    """

    def __init__(self, source: Optional[DataThread] = None, datarate: int = 60, num_data_points: int = 100, y_max: int = 10, y_min: int = 10):
        super().__init__()
        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timeout)
        self.time_last = time.time()
        self.source = source
        self.set_params(datarate, num_data_points, y_max, y_min)

    def set_params(self, datarate: int = 60, num_data_points: int = 100, y_max: int = 10, y_min: int = 10):
        print(f"setting params {datarate, num_data_points, y_max, y_min}")
        self.timer.setInterval(int(1000/datarate))
        self.data = Queue(maxsize=num_data_points)
        self.num_data_points = num_data_points
        [self.data.put(0) for _ in range(self.num_data_points)]
        self.y_max = y_max
        self.y_min = y_min
        self.setup_UI()

    def set_source(self, source: DataThread):
        self.source = source
        self.thread = QThread()
        self.source.moveToThread(self.thread)
        self.thread.start()
        self.frame_changed.connect(self.source.get_value)
        self.source.value.connect(self.generate_data)

    def on_timeout(self):
        self.counter += 1
        self.frame_changed.emit(self.counter)
    
    # invoke externally
    def start(self):
        print("Starting in data plot")
        self.counter = 0
        self.last_frames = 0
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def setup_UI(self):
        print("Setup UI")
        pg.setConfigOption('background', 0.95)
        self.setYRange(self.y_min, self.y_max)
        self.plots = []
        p_item = self.getPlotItem()
        if p_item is not None:
            self.plot = p_item.plot([], [], pen=pg.mkPen("r", width=2))
        # self.frame_changed.connect(self.frame_rate)

    '''
    Currently, on timeout:
        We increase counter and emit the counter value to the source 
        The source will then emit the value it currently has which will then 
        be added to the queue to be displayed in the graph
    '''
    @pyqtSlot(float)
    def generate_data(self, i):
        self.data.get()
        self.data.put(i)
        self.plot_data(range(len(self.data.queue)), self.data.queue)            

    def plot_data(self, spaces, data):
        self.plot.setData(spaces, data)

    @pyqtSlot()
    def restart(self):
        self.data = Queue()
        [self.data.put(0) for _ in range(self.num_data_points)]

    @pyqtSlot(int)
    def frame_rate(self, frames):
        if time.time() - self.time_last > 1:
            print(f"{self.source} FPS: {frames - self.last_frames}")
            self.last_frames = frames
            self.time_last = time.time()

    def cleanup(self):
        print("cleanup")
        self.source.cleanup()

    def send_value(self, value: bytes):
        self.source.send_value(value)

if __name__ == "__main__":
    config = {
            "plot_name": "name",
            "sources" : [
                {
                    "device_name": "Thingy",
                    "service_name": "Battery Service",
                    "pen_color": "FFFF00",
                    "encoding":  [
                        {
                            "length" : 32,
                            "signed" : True,
                            "remainder": 16,
                            },
                        ],
                    "data_points": [0],
                    },
                ],
            "data_rate": 60,
            "num_data_points": 100,
            "y_max": 1,
            "y_min": -1,
            "x_label": "time",
            "x_units": "s",
            "y_label": "speed",
            "y_units": "m/s",
            }
    source = config["sources"][0]
    app = QApplication(sys.argv)
    win = pg.GraphicsLayoutWidget(show = True, title = "Config based plots")

    sin_plot = win.addPlot(title="Sin Graph")
    curve = sin_plot.plot(pen='y')
    # curve = sin_plot.plot(pen=hex_to_rgb(source["pen_color"]))
    sin_plot.setLabel('left', config.get("y_label", ""), units=config.get("y_units", ""))
    sin_plot.setLabel('bottom', config.get("x_label", ""), units=config.get("x_units", ""))
    sin_plot.enableAutoRange('y', False)
    sin_plot.setRange(yRange=(config["y_min"], config["y_max"]))
    data = Queue(maxsize=config.get("num_data_points", 100))
    [data.put(0) for _ in range(config.get("num_data_points", 100))]
    curve.setData(data.queue)
    time_last = time.time()

    def update_data(val):
        global data
        data.get()
        data.put(val)

    def update_plot():
        global curve, data, time_last
        curve.setData(data.queue)
        print(1/(time.time() - time_last))
        time_last = time.time()

    def sin_func(a, b, c, d, data):
        return (a*math.sin(b*data+c)+d)

    sink = coro(update_data)
    sink.__next__()
    source = coro(functools.partial(sin_func, 1, 1, 0, 0), sink)
    source.__next__()
    get_time = coro(time.time, source)
    get_time.__next__()

    timer = QTimer()
    timer.setInterval(int(1000/60))
    timer.timeout.connect(functools.partial(get_time.send, None))
    timer.timeout.connect(update_plot)
    timer.start()
    app.exec()

    '''
p5 = win.addPlot(title="Scatter plot, axis labels, log scale")
x = np.random.normal(size=1000) * 1e-5
y = x*1000 + 0.005 * np.random.normal(size=1000)
y -= y.min()-1.0
mask = x > 1e-15
x = x[mask]
y = y[mask]
p5.plot(x, y, pen=None, symbol='t', symbolPen=None, symbolSize=10, symbolBrush=(100, 100, 255, 50))
p5.setLabel('left', "Y Axis", units='A')
p5.setLabel('bottom', "Y Axis", units='s')
p5.setLogMode(x=True, y=False)

p6 = win.addPlot(title="Updating plot")
curve = p6.plot(pen='y')
data = np.random.normal(size=(10,1000))
ptr = 0
def update():
    global curve, data, ptr, p6
    curve.setData(data[ptr%10])
    if ptr == 0:
        p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    ptr += 1
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)
    '''



