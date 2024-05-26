import functools
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

from src.ble.threads import DataThread
from src.ble.ble_generators import NotifyThread

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
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    # mw = QWidget()
    # mw.show()
    # client = BleakClient("F1:EC:95:17:0A:62")
    # print("Connecting to client")
    # connection_task = loop.create_task(client.connect())
    # connection_task.add_done_callback(lambda _: print("connected"))
    # UUID = "EF680409-9B35-4933-9B10-52FFA9740042"
    # thread = NotifyThread(client, UUID)
    # pw = DataPlot(thread)
    pw = TrayItem({}, {})
    pw.show()
    loop.run_forever()
    # sys.exit(app.exec())

