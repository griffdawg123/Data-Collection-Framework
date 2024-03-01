from logging import Logger
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
import json
import string

from windows.config_selection import ConfigSelection

class Workspace(QWidget):
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.config_path: str = None
        self.config: dict = None
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
        self.title.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.layout: QHBoxLayout = QHBoxLayout()
        self.layout.addWidget(self.title)
        self.setLayout(self.layout)

    def load_config(self) -> dict:
        self.config_window = ConfigSelection(self.logger, self.read_config)
        self.config_window.show()
        self.hide()

    def get_title(self) -> str:
        if self.config is None:
            return "Data Acquisition Framework"
        else:
            return self.config["name"]

    
    