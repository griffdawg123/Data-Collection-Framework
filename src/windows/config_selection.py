from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFileDialog
import logging
import json
from src.windows.new_config import NewConfig
from src.windows.load_config import LoadConfig
import src.helpers
from pathlib import Path

class ConfigSelection(QWidget):
    def __init__(self, logger: logging.Logger, set_config_path: Callable[[str], None]) -> None:
        super().__init__()
        self.logger = logger
        self.set_config_func = set_config_path
        self.init_UI()

    def init_UI(self) -> None:
        self.setWindowTitle("Data Collection Framework")
        self.resize(720, 540)
        src.helpers.center(self)

        self.new_button = QPushButton(parent=self, text="New Workspace")
        self.new_button.setFixedSize(250, 75)
        self.new_button.clicked.connect(self.new_clicked)

        self.load_button = QPushButton(parent=self, text="Load Workspace")
        self.load_button.setFixedSize(250, 75)
        self.load_button.clicked.connect(self.load_clicked)


        layout: QVBoxLayout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.new_button)
        layout.addWidget(self.load_button)
        layout.addStretch()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

    def new_clicked(self):
        self.logger.debug("New Workspace Button Clicked")
        Path("config/workspaces").mkdir(parents=True, exist_ok=True)

        new_workspace_dialogue = NewConfig()
        success, new_workspace_filename = new_workspace_dialogue.get_file_name()
        if success:
            self.logger.info("New Workspace Successful")
            with open(f"config/workspaces/{src.helpers.format_config_name(new_workspace_filename)}.config", "w+") as new_file:
                json_config = {}
                json_config["name"] = new_workspace_filename
                json_config["devices"] = []
                json_config["plots"] = { "rows": [], "data_rate": 60}
                new_file.write(json.dumps(json_config))
            self.logger.info(f"New workspace created with name: {new_workspace_filename}")
            self.config_url = f"config/workspaces/{src.helpers.format_config_name(new_workspace_filename)}.config"
            self.set_config_func(self.config_url)
            self.close()
        else:
            self.logger.info("New Workspace Canceled")
        
    def load_clicked(self):
        self.logger.info("Workspace Config Loaded")
        config_name, _ = QFileDialog.getOpenFileName(self,self.tr("Open Config"), "./config/workspaces/", self.tr("Config Files (*.config)"))
        if config_name:
            self.config_url = f"config/workspaces/{config_name.split('/')[-1]}"
            self.set_config_func(self.config_url)
            self.close()
