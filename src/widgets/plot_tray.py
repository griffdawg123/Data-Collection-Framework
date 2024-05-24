from typing import Dict, List
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from src.widgets.control_buttons import ControlButtons
from src.widgets.data_plot import DataPlot

class PlotTray(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.scroll_area = QScrollArea()
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()

        self.control_buttons = ControlButtons()

    def init_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.control_buttons)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

    def set_plots(self, plot_configs: List):
        layout = QVBoxLayout()
        for conf in plot_configs:
            self.add_plot(conf, layout)
        self.scroll_widget.setLayout(layout)
        self.scroll_area.setWidget(self.scroll_widget)

    # add a new plot to the tray when the new plot button is clicked
    def add_plot(self, config: Dict, layout: QVBoxLayout):
        new_plot = DataPlot(config)
        layout.addWidget(new_plot)

    # remove a new plot when a button is clicked
    def remove_plot(self):
        return

    # initially setting of clients when workspace is loaded
    def set_clients(self):
        return

    # add a new client when a new one is added to the workspace
    def add_client(self):
        return

    # remove a client from all plots when it is removed from the workspace
    def remove_client(self):
        return

    
