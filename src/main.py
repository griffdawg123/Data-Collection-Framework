from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
import numpy as np

# https://stackoverflow.com/questions/53573670/animated-charts-in-pyqtgraph

class TimeLine(QtCore.QObject):
    frameChanged = QtCore.pyqtSignal(int)

    def __init__(self, interval=60, loopCount=1, parent=None):
        super(TimeLine, self).__init__(parent)
        self._startFrame = 0
        self._endFrame = 0
        self._loopCount = loopCount
        self._timer = QtCore.QTimer(self, timeout=self.on_timeout)
        self._counter = 0
        self._loop_counter = 0
        self.setInterval(interval)

    def on_timeout(self):
        if self._startFrame <= self._counter < self._endFrame:
            self.frameChanged.emit(self._counter)
            self._counter += 1
        else:
            self._counter = 0
            self._loop_counter += 1

        if self._loopCount > 0: 
            if self._loop_counter >= self.loopCount():
                self._timer.stop() 

    def setLoopCount(self, loopCount):
        self._loopCount = loopCount

    def loopCount(self):
        return self._loopCount

    interval = QtCore.pyqtProperty(int, fget=loopCount, fset=setLoopCount)

    def setInterval(self, interval):
        self._timer.setInterval(interval)

    def interval(self):
        return self._timer.interval()

    interval = QtCore.pyqtProperty(int, fget=interval, fset=setInterval)

    def setFrameRange(self, startFrame, endFrame):
        self._startFrame = startFrame
        self._endFrame = endFrame

    @QtCore.pyqtSlot()
    def start(self):
        self._counter = 0
        self._loop_counter = 0
        self._timer.start()


class Gui(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        pg.setConfigOption('background', 0.95)
        pg.setConfigOptions(antialias=True)
        self.plot = pg.PlotWidget()
        self.plot.setAspectLocked(lock=True, ratio=0.01)
        self.plot.setYRange(-3, 3)
        widget_layout = QtWidgets.QVBoxLayout(self)
        widget_layout.addWidget(self.plot)

        self._plots = [self.plot.plot([], [], pen=pg.mkPen(color=color, width=2)) for color in ("g", "r", "y")]
        self._timeline = TimeLine(loopCount=0, interval=10)
        self._timeline.setFrameRange(0, 720)
        self._timeline.frameChanged.connect(self.generate_data)
        self._timeline.start()

    def plot_data(self, data):
        for plt, val in zip(self._plots, data):
            plt.setData(range(len(val)), val)

    @QtCore.pyqtSlot(int)
    def generate_data(self, i):
        ang = np.arange(i, i + 720)
        cos_func = np.cos(np.radians(ang)) 
        sin_func = np.sin(np.radians(ang))
        tan_func = sin_func/cos_func
        tan_func[(tan_func < -3) | (tan_func > 3)] = np.NaN
        self.plot_data([sin_func, cos_func, tan_func])

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    gui = Gui()
    gui.show()
    sys.exit(app.exec_())