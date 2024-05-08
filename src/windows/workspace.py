from logging import Logger
import logging
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QVBoxLayout, QApplication, QHBoxLayout, QFileDialog
from PyQt6.QtCore import Qt
import json
import string
import asyncio

from bleak import BleakClient
from qasync import asyncClose
from src.loaders.config_loader import ConfigLoader
from src.widgets.data_plot import DataPlot
from src.ble.static_generators import RandomThread, SinThread
from src.widgets.status_tray import StatusTray
from src.windows.config_selection import ConfigSelection
from src.ble.ble_generators import NotifyThread, ReadThread
from src.windows.new_device import NewDevice
from src.widgets.graph_widget import PlotWidget
from src.logs.logs_setup import LoggerEnv

class Workspace(QWidget):
    def __init__(self, log_level: LoggerEnv) -> None:
        super().__init__()
        self.config_path: str = ""
        self.clients = {}
        self.logger = logging.getLogger(log_level)
        self.config_manager = None
        # calls read_config with the config path
        self.config_window: ConfigSelection = ConfigSelection(self.logger, self.read_config)
        self.config_window.show()
        self.hide()

    def read_config(self, config_path: str) -> None:
        self.config_manager = ConfigLoader(config_path)
        self.load_UI()
        self.showMaximized()

    def load_UI(self) -> None:
        if self.config_manager is not None:
            self.clients = self.config_manager.load_device_managers()
        self.status_tray = StatusTray(self.clients, self.remove_device)

        self.header: QWidget = QWidget()
        self.header_layout = QVBoxLayout()
        self.title: QLabel = QLabel()
        self.title.setText(string.capwords(self.get_title()))
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.title.setStyleSheet("border: 1px solid black; font-size: 40px;")
        self.header_layout.addWidget(self.title)

        self.control_buttons = QWidget()
        self.control_buttons.setFixedWidth(self.width()//2)
        self.save_button = QPushButton("Save Setup")
        self.play_button = QPushButton(">")
        self.pause_button = QPushButton("||")
        self.control_layout = QHBoxLayout()
        self.control_layout.addWidget(self.save_button)
        self.control_layout.addWidget(self.play_button)
        self.control_layout.addWidget(self.pause_button)
        self.control_buttons.setLayout(self.control_layout)
        self.header_layout.addWidget(self.control_buttons)

        self.header.setLayout(self.header_layout) 

        self.setup_column: QWidget = QWidget()
        self.setup_column.setStyleSheet("border: 1px solid black;")
        self.setup_column_label: QLabel = QLabel()
        self.setup_column_label.setText("Setup Column")
        self.setup_column_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.plots = QWidget()
        self.plots_layout = QVBoxLayout()
        self.graph = PlotWidget(self.clients)
        self.graph.set_plot_params(y_max=360, y_min=0)
        self.plots_layout.addWidget(self.graph)
        self.plots.setLayout(self.plots_layout)
        self.plots.setStyleSheet("border: 1px solid black; font-size: 40px;")

        self.save_button.clicked.connect(self.graph.set_plot_thread)
        self.play_button.clicked.connect(self.graph.start)
        self.pause_button.clicked.connect(self.graph.stop)

        self.new_device_button = QPushButton("New Device")
        self.new_device_button.clicked.connect(self.new_device)

        self.load_device_button = QPushButton("Load Device")
        self.load_device_button.clicked.connect(self.load_device)

        self.restart_button = QPushButton()
        self.restart_button.setText("Restart")
        
        self.setup_column_layout = QVBoxLayout()
        self.setup_column_layout.addWidget(self.setup_column_label)
        self.setup_column_layout.addWidget(self.status_tray)
        self.setup_column_layout.addWidget(self.new_device_button)
        self.setup_column_layout.addWidget(self.load_device_button)
        self.setup_column_layout.addWidget(self.restart_button)
        self.setup_column.setLayout(self.setup_column_layout)

        self.title_layout: QVBoxLayout = QVBoxLayout()
        self.title_layout.addWidget(self.header)

        self.workspace_layout: QHBoxLayout = QHBoxLayout()
        self.workspace_layout.addWidget(self.setup_column)
        self.workspace_layout.addWidget(self.plots)
        self.workspace_layout.setStretch(0, 1)
        self.workspace_layout.setStretch(1, 9)
        self.workspace = QWidget()
        self.workspace.setLayout(self.workspace_layout)

        self.title_layout.addWidget(self.workspace)
        self.title_layout.setStretch(0, 1)
        self.title_layout.setStretch(1, 9)

        self.setLayout(self.title_layout)

    def load_config(self) -> None:
        self.config_window = ConfigSelection(self.logger, self.read_config)
        self.config_window.show()
        self.hide()

    def get_title(self) -> str:
        if self.config_manager is None:
            return "Data Acquisition Framework"
        else:
            return self.config_manager.get_config_name()
        
    def new_device(self) -> None:
        new_dialog = NewDevice()
        if new_dialog.exec():
            name, address = new_dialog.get_text()
            if self.config_manager is not None:
                self.config_manager.save_device(name, address)
        if self.config_manager is not None:
            self.clients = self.config_manager.load_device_managers()
            self.status_tray.add_device(name, address)

    def load_device(self) -> None:
        config_path, _ = QFileDialog.getOpenFileName(self,self.tr("Open Config"), "./config/devices/", self.tr("Config Files (*.config)"))
        new_device = {}
        if config_path:
            if self.config_manager is not None:
                self.config_manager.load_device(config_path)
            with open(config_path, "r") as infile:
                new_device = json.loads(infile.read())
        if self.config_manager is not None:
            self.clients = self.config_manager.load_device_managers()
            if new_device:
                self.status_tray.add_device(new_device["name"], new_device["address"])
        print("clients", self.clients)

    # remove device from device dictionary and then delete from config
    def remove_device(self, device_name):
        loop = asyncio.get_event_loop()
        disconnect_task = loop.create_task(self.clients[device_name].disconnect())
        if self.config_manager is not None:
            self.config_manager.remove_device(device_name)
            self.clients = self.config_manager.load_device_managers()
        print("clients ", self.clients)


    async def disconnect_from_clients(self):
        for client in self.clients.values():
            await client.disconnect()


    @asyncClose
    async def closeEvent(self, event):
        # TODO write config to file
        await self.disconnect_from_clients()

