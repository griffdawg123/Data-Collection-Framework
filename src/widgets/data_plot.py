import time
from PyQt6.QtCore import QTimer, pyqtSignal, pyqtSlot, QThread
from queue import Queue
import pyqtgraph as pg
import os
import sys

# append path directory to system path so other modules can be accessed
myDir = os.getcwd()
sys.path.append(myDir)
from pathlib import Path
path = Path(myDir)
a=str(path.parent.absolute())
sys.path.append(a)
from src.ble.threads import DataThread

class DataPlot(pg.PlotWidget):

    frame_changed = pyqtSignal(int)

    """
    interval : 60 ms secs / frame
    framerate : # frames / sec
    """

    def __init__(self, source: DataThread, datarate: int = 60, num_data_points: int = 100, y_max: int = 10, y_min: int = 10):
        super().__init__()
        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(int(1000/datarate))
        self.timer.timeout.connect(self.on_timeout)
        self.data = Queue(maxsize=num_data_points)
        self.time_last = time.time()
        self.source = source
        self.thread = QThread()
        self.source.moveToThread(self.thread)
        self.thread.start()
        self.num_data_points = num_data_points
        [self.data.put(0) for _ in range(self.num_data_points)]
        self.y_max = y_max
        self.y_min = y_min
        self.setup_UI()

    def on_timeout(self):
        self.counter += 1
        self.frame_changed.emit(self.counter)

    def start(self):
        self.counter = 0
        self.last_frames = 0
        self.timer.start()

    def setup_UI(self):
        pg.setConfigOption('background', 0.95)
        self.setYRange(self.y_min, self.y_max)
        self.plots = []
        p_item = self.getPlotItem()
        if p_item is not None:
            self.plot = p_item.plot([], [], pen=pg.mkPen("r", width=2))
        self.frame_changed.connect(self.source.get_value)
        self.frame_changed.connect(self.frame_rate)
        self.source.value.connect(self.generate_data)
        self.start()

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
        
    