import time
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, pyqtSignal, pyqtSlot, QThread
from typing import Generator, List, Any, NoReturn, Tuple
from queue import Queue
import pyqtgraph as pg
from itertools import islice
import os
import sys

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

    def __init__(self, source: Generator[float, None, None], datarate: int = 60, num_data_points: int = 100, y_max: int = 10, y_min: int = 10):
        super().__init__()
        self.counter = 0
        self.timer = QTimer()
        self.timer.setInterval(int(1000/datarate))
        self.timer.timeout.connect(self.on_timeout)
        self.data = Queue()
        self.start_time = time.time()
        self.source = source
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
        self.timer.start()

    def setup_UI(self):
        pg.setConfigOption('background', 0.95)
        pg.setConfigOptions(antialias=True)
        self.setYRange(self.y_min, self.y_max)
        self.plots = []
        p_item = self.getPlotItem()
        if p_item is not None:
            self.plot = p_item.plot([], [], pen=pg.mkPen("r", width=2))
        self.frame_changed.connect(self.generate_data) # on frame change, call get value function
        self.start()

    @pyqtSlot(int)
    def generate_data(self, i):
        self.data.put(next(self.source))
        self.plot_data(range(len(self.data.queue)), self.data.queue)
        while len(self.data.queue) > 100:
            self.data.get()

    def plot_data(self, spaces, data):
        self.plot.setData(spaces, data)
    