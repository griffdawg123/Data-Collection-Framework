import time
from typing import Optional
from PyQt6.QtCore import QTimer, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtWidgets import QApplication, QWidget
from bleak import BleakClient
from queue import Queue
import pyqtgraph as pg
import os
import sys
from qasync import QEventLoop
import asyncio

from src.ble.threads import DataThread
from src.ble.ble_generators import NotifyThread

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
    client = BleakClient("F1:EC:95:17:0A:62")
    print("Connecting to client")
    connection_task = loop.create_task(client.connect())
    connection_task.add_done_callback(lambda _: print("connected"))
    UUID = "EF680409-9B35-4933-9B10-52FFA9740042"
    thread = NotifyThread(client, UUID)
    pw = DataPlot(thread)
    pw.show()
    loop.run_forever()
    # sys.exit(app.exec())

