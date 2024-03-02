from logging import Logger
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
import json
import string
import sys
import os
myDir = os.getcwd()
sys.path.append(myDir)
from pathlib import Path
path = Path(myDir)
a=str(path.parent.absolute())
sys.path.append(a)
from src.widgets.data_plot import DataPlot
from src.ble.sin_generator import get_sin

from windows.config_selection import ConfigSelection

class Workspace(QWidget):
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.config_path: str = ""
        self.config: dict = {}
        self.logger = logger
        self.config_window: ConfigSelection = ConfigSelection(self.logger, self.read_config)
        self.config_window.show()

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
        
        self.setup_column: QLabel = QLabel()
        self.setup_column.setText("Setup Column")
        self.setup_column.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setup_column.setStyleSheet("border: 1px solid black;")

        self.graphs: DataPlot = DataPlot(get_sin(), y_max=1, y_min=-1, datarate=100)

        self.layout: QGridLayout = QGridLayout()
        self.layout.addWidget(self.title, 0, 0, 1, 4)
        self.layout.addWidget(self.setup_column, 1, 0, 9, 1)
        self.layout.addWidget(self.graphs, 1, 1, 9, 3)
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

    
    