from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDialog
import logging
import json
from windows.new_config import NewConfig
import helpers

class Landing(QWidget):
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()
        self.logger = logger
        self.init_gui()

    def init_gui(self) -> None:
        self.setWindowTitle("Data Collection Framework")
        self.resize(720, 540)
        helpers.center(self)

        self.new_button = QPushButton(parent=self, text="New Workspace")
        self.new_button.setFixedSize(250, 75)
        self.new_button.clicked.connect(self.new_clicked)

        self.load_button = QPushButton(parent=self, text="Load Workspace")
        self.load_button.setFixedSize(250, 75)
        self.load_button.clicked.connect(self.load_clicked)


        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.new_button)
        self.layout.addWidget(self.load_button)
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

    def new_clicked(self):
        self.logger.debug("New Workspace Button Clicked")

        new_workspace_dialogue = NewConfig()
        success, new_workspace_filename = new_workspace_dialogue.get_file_name()
        if success:
            self.logger.info("New Workspace Successful")
            with open(f"config/workspaces/{new_workspace_filename}.config", "w+") as new_file:
                json_config = {}
                json_config["name"] = new_workspace_filename
                new_file.write(json.dumps(json_config))
            self.logger.info(f"New workspace created with name: {new_workspace_filename}")
        else:
            self.logger.info("New Workspace Canceled")
        
    def load_clicked(self):
        self.logger.info("Workspace Config Loaded")