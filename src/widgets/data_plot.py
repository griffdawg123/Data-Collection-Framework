import functools
from typing import List, Optional
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication
from queue import Queue
import pyqtgraph as pg
import sys
from bleak import BleakClient

from src.ble.static_generators import func_coro, param_cos, param_sin, sink_coro, source_coro
from src.helpers import hex_to_rgb, parse_bytearray
from src.loaders.datastream_manager import DatastreamManager
from src.loaders.device_manager import DeviceManager

class Plots(pg.GraphicsLayoutWidget):

    graph_refresh = pyqtSignal()

    def __init__(self, config):
        super().__init__(show=True, title=config.get("title", ""))
        self.funcs = {
            "sin" : param_sin,
            "cos" : param_cos,
        }
        self.config = config
        self.dm: DeviceManager = DeviceManager()
        self.dm.connect_notify_done(self.timer_control)

        self.datastreams: DatastreamManager = DatastreamManager()
        self.notify_tasks: List = []
        self.plot_information = []
        self.init_rows(config.get("rows", []))
        self.timer = QTimer()

        # 1000/60 --> 60 fps
        self.timer.setInterval(int(1000/config.get("data_rate", 60)))
        self.init_timers()
    
    def init_rows(self, plot_configs):
        for i, row in enumerate(plot_configs):
            self.plot_information.append([])
            self.init_plots(row, i)
            self.nextRow()

    def init_plots(self, row, i):
        for j, plot in enumerate(row):
            self.plot_information[i].append([])
            new_plot = self.addPlot(title=plot.get("title"))
            new_plot.setLabel('left', plot.get("y_label", ""), units=plot.get("y_units", ""))
            new_plot.setLabel('bottom', plot.get("x_label", ""), units=plot.get("x_units", ""))
            new_plot.enableAutoRange('y', False)
            new_plot.setRange(yRange=(plot.get("y_min", 0), plot.get("y_max", 100)))
            
            num_data_points = plot.get("num_data_points", 100)
            self.init_plotlines(new_plot, plot.get("plotlines", []), num_data_points, i, j)

    def init_plotlines(self, plot: pg.PlotItem, plotlines, datapoints, i, j):
        for k, plotline in enumerate(plotlines):
            queue = Queue(maxsize=datapoints)
            [ queue.put(0) for _ in range(datapoints) ]
            # When sink receives a value, it will update the queue at [i,j,k]
            sink = sink_coro(functools.partial(self.update_data, i, j, k))
            next(sink)
            # When func receives a value, it will calculate the new value and pass it to sink
            func = func_coro(
                    functools.partial(
                        self.funcs.get(plotline.get("func", {}).get("type"), lambda x: x),
                        plotline.get("func", {}).get("params", {})
                    ),
                    sink
                    )
            next(func)

            # TODO: Make it so data_source gets sent a value every time the timer 
            # activates

            source_type = plotline.get("source", "Time")
            if source_type not in self.notify_tasks:
                self.notify_tasks.append(source_type)
                # Set up ble

            data_source = source_coro(func, index=plotline.get("chunk", 0))
            next(data_source)
            
            color = plotline.get("pen_color", "FFFFFF") 
            curve = plot.plot(pen=hex_to_rgb(color))
            curve.setData(queue.queue)

            
            source_info = {
                "data" : queue,
                "sink" : sink,
                "func" : func,
                "source" : data_source,
                "curve" : curve,
                # "client" : client,
                "color" : color,
                "type" : source_type,
            }
            self.plot_information[i][j].append(source_info)

    def update_data(self, i, j, k, data):
        # update then queue of this data
        queue: Queue = self.plot_information[i][j][k].get("data")
        queue.get()
        queue.put(data)

    def update_plots(self):
        for i, row in enumerate(self.plot_information):
            for j, plot_confs in enumerate(row):
                plot: pg.PlotItem = self.getItem(i, j)
                plot.clear()
                for conf in plot_confs:
                    curve = plot.plot(pen=hex_to_rgb(conf["color"]))
                    curve.setData(conf["data"].queue)
                    
    # def on_timeout(self, source):
    #     next(source)

    def on_new_data(self, source, value):
        for row in self.plot_information:
            for plot in row:
                for source_config in plot:
                    if source_config.get("type") == source:
                        source_config["source"].send(value)


    def init_timers(self):
        # for row in self.plot_information:
        #     for plot in row:
        #         for source in plot:
        #             print("Plot")
        #             self.timer.timeout.connect(functools.partial(self.on_timeout, source["source"]))
        #             print("Sending to source", source)
        # on timeout, emits all values
        self.timer.timeout.connect(self.datastreams.source_update)
        self.timer.timeout.connect(self.update_plots)
        self.datastreams.connect_to_signal(self.on_new_data)


    def restart(self):
        for row in self.plot_information:
            for plot in row:
                for source in plot:
                    datapoints = len(source["data"].queue)
                    queue = Queue(maxsize=datapoints)
                    [ queue.put(0) for _ in range(datapoints) ]
                    source["data"] = queue
        self.update_plots()

    def stop(self):
        self.dm.stop_notify()

    def start_clicked(self):
        print(f"Notify Tasks: {self.notify_tasks}")
        self.dm.start_notify(self.notify_tasks)

    def timer_control(self, start: bool):
        '''
        Start clicked sends a signal to the device manager to try to start 
        notify for all of the needed devices/characteristics
        When all are done - start timer.
        '''
        if start:
            self.timer.start()
        else:
            self.timer.stop()

