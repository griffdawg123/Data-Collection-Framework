from logging import Logger
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt
import json
import string
import sys
import os

# append path directory to system path so other modules can be accessed
myDir = os.getcwd()
sys.path.append(myDir)
from pathlib import Path
path = Path(myDir)
a=str(path.parent.absolute())
sys.path.append(a)
from src.widgets.data_plot import DataPlot
from src.ble.static_generators import RandomThread, SinThread
from src.windows.config_selection import ConfigSelection
from src.ble.ble_generators import NotifyThread, ReadThread

class Workspace(QWidget):
    def __init__(self, logger: Logger, app: QApplication) -> None:
        super().__init__()
        self.app = app
        self.config_path: str = ""
        self.config: dict = {}
        self.logger = logger
        self.config_window: ConfigSelection = ConfigSelection(self.logger, self.read_config)
        self.config_window.show()
        self.hide()

    def read_config(self, config_path: str) -> None:
        with open(config_path, "r") as infile:
            self.config = json.loads(infile.read())
        self.load_UI()
        self.showMaximized()

    def load_UI(self) -> None:
        self.setWindowTitle(self.get_title())

        self.title: QLabel = QLabel()
        self.title.setText(string.capwords(self.get_title()))
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.title.setStyleSheet("border: 1px solid black; font-size: 40px;")
        
        self.setup_column: QWidget = QWidget()
        self.setup_column.setStyleSheet("border: 1px solid black;")
        self.setup_column_label: QLabel = QLabel()
        self.setup_column_label.setText("Setup Column")
        self.setup_column_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # self.sin_graph: DataPlot = DataPlot(SinThread(), y_max=1, y_min=-1, datarate=50)
        # self.rand_graph: DataPlot = DataPlot(RandomThread(), y_min=0, y_max=1, datarate=50)
        # self.battery_graph: DataPlot = DataPlot(ReadThread("F1:EC:95:17:0A:62", "00002a19-0000-1000-8000-00805f9b34fb"), y_min=0, y_max=100, datarate=1)

        self.pitch = DataPlot(NotifyThread("F1:EC:95:17:0A:62", "EF680407-9B35-4933-9B10-52FFA9740042"), y_min=0, y_max=360, datarate=200)
        self.yaw = DataPlot(NotifyThread("F1:EC:95:17:0A:62", "EF680407-9B35-4933-9B10-52FFA9740042"), y_min=0, y_max=360, datarate=200)
        self.roll = DataPlot(NotifyThread("F1:EC:95:17:0A:62", "EF680407-9B35-4933-9B10-52FFA9740042"), y_min=0, y_max=360, datarate=200)

        self.restart_button = QPushButton()
        self.restart_button.setText("Restart")
        # self.restart_button.clicked.connect(self.sin_graph.restart)
        # self.restart_button.clicked.connect(self.rand_graph.restart)
        
        self.setup_column_layout = QVBoxLayout()
        self.setup_column_layout.addWidget(self.setup_column_label)
        self.setup_column_layout.addWidget(self.restart_button)
        self.setup_column.setLayout(self.setup_column_layout)

        self.layout: QGridLayout = QGridLayout()
        self.layout.addWidget(self.title, 0, 0, 1, 4)
        self.layout.addWidget(self.setup_column, 1, 0, 9, 1)
        self.layout.addWidget(self.pitch, 1, 1, 3, 3)
        self.layout.addWidget(self.yaw, 1, 1, 3, 3)
        self.layout.addWidget(self.roll, 1, 1, 3, 3)
        # self.layout.addWidget(self.sin_graph, 1, 1, 5, 3)
        # self.layout.addWidget(self.rand_graph, 6, 1, 5, 3)
        self.setLayout(self.layout)

    def load_config(self) -> None:
        self.config_window = ConfigSelection(self.logger, self.read_config)
        self.config_window.show()
        self.hide()

    def get_title(self) -> str:
        if self.config is None:
            return "Data Acquisition Framework"
        else:
            return self.config["name"]

    
    