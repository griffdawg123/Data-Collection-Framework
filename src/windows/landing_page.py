from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDialog
import logging
import json
from windows.new_config import NewConfig

class Landing(QWidget):
    def __init__(self, logger: logging.Logger) -> None:
        super().__init__()
        self.logger = logger
        self.init_gui()

    def init_gui(self) -> None:
        self.setWindowTitle("Data Collection Framework")
        self.resize(720, 540)
        self.center()

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

    def center(self) -> None:
        screen_rect = self.frameGeometry()
        screen_geometry = self.screen().availableGeometry()
        centre_point = screen_geometry.center()
        screen_rect.moveCenter(centre_point)
        self.move(screen_rect.topLeft())


    def new_clicked(self):
        self.logger.debug("New Workspace Button Clicked")

        new_workspace_dialogue = NewConfig()
        if new_workspace_dialogue.exec():
            self.logger.info("New Workspace Successful")
            workspace_name = "new_config"
            with open("config/workspaces/newfile.json", "w+") as new_file:
                json_config = {}
                json_config["name"] = workspace_name
                new_file.write(json.dumps(json_config))
            self.logger.info(f"New workspace created with name: {workspace_name}")
        else:
            self.logger.info("New Workspace Canceled")
        
    def load_clicked(self):
        self.logger.info("Workspace Config Loaded")