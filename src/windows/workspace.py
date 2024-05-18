from logging import Logger
import logging
from typing import Dict
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QPushButton,
    QVBoxLayout,
    QApplication,
    QHBoxLayout,
    QFileDialog
)
from PyQt6.QtCore import Qt
import json
import string
import asyncio

from bleak import BleakClient
from qasync import asyncClose
from src import helpers
from src.loaders.config_loader import ConfigLoader
from src.widgets.data_plot import DataPlot
from src.ble.static_generators import RandomThread, SinThread
from src.widgets.header import Header
from src.widgets.setup_column import SetupColumn
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
        self.tasks = set()
        self.clients: Dict[str, BleakClient] = {}
        self.logger = logging.getLogger(log_level)
        self.logger.info("Logger Enabled")
        default_config = "src/loaders/default.config"
        self.config_manager = ConfigLoader(default_config, self.logger)
        self.config = self.config_manager.load_config()
        self.status_tray = StatusTray(self.remove_device)
        self.header = QWidget()
        self.setup_column = QWidget()
        self.config_window: ConfigSelection = ConfigSelection(
            self.logger,
            self.create_config_manager
        )
        self.config_window.show()
        self.hide()

    def create_config_manager(self, config_path: str) -> None:
        self.config_manager = ConfigLoader(config_path, self.logger)
        self.config = self.config_manager.load_config()
        self.load_UI()
        self.showMaximized()

    def load_UI(self) -> None:
        self.clients = self.config_manager.load_devices()
        self.config["devices"] = [
            helpers.format_config_name(device_name)
            for device_name in self.clients.keys()
        ]
        self.status_tray = StatusTray(self.remove_device, self.clients)
        self.new_device_button = QPushButton("New Device")
        self.new_device_button.clicked.connect(self.new_device)
        self.load_device_button = QPushButton("Load Device")
        self.load_device_button.clicked.connect(self.load_device)
        self.restart_button = QPushButton()
        self.restart_button.setText("Restart")
        self.setup_column = SetupColumn(
            self.status_tray,
            self.new_device_button,
            self.load_device_button,
            self.restart_button
        )

        self.plots = QWidget()
        self.plots_layout = QVBoxLayout()
        self.graph = PlotWidget(self.clients)
        self.graph.set_plot_params(y_max=360, y_min=0)
        self.plots_layout.addWidget(self.graph)
        self.plots.setLayout(self.plots_layout)
        self.plots.setStyleSheet("border: 1px solid black; font-size: 40px;")

        self.header = Header(self.config_manager.get_title())
        self.header.setup_buttons(
            self.graph.set_plot_thread,
            self.graph.start,
            self.graph.stop
        )

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
        self.logger.info("UI Loaded")

    def add_device(self, conf):
        client = BleakClient(conf["address"])
        self.clients[conf["name"]] = client
        self.add_device_to_conf(conf["name"])
        self.status_tray.add_device(conf["name"], client)

    def add_device_to_conf(self, device_name):
        devices = self.config["devices"]
        devices.append(helpers.format_config_name(device_name))
        self.config["devices"] = devices

    def remove_device_from_conf(self, device_name):
        devices = self.config["devices"]
        devices.remove(helpers.format_config_name(device_name))
        self.config["devices"] = devices

    # create new device from input
    # create new config file and add name to config
    def new_device(self) -> None:
        new_dialog = NewDevice()
        if new_dialog.exec():
            name, address = new_dialog.get_text()
            device_config = {
                "name": name,
                "address": address
            }
            self.config_manager.save_device(device_config)
            self.logger.info(
                f"New device with name {name} and address {address}"
            )
            self.add_device(device_config)

    # load device from existing file
    # add file name to config
    def load_device(self) -> None:
        config_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Open Config"),
            "./config/devices/",
            self.tr("Config Files (*.config)")
        )
        new_device = {}
        if config_path:
            with open(config_path, "r", encoding="utf8") as infile:
                new_device = json.loads(infile.read())
                self.add_device(new_device)
                new_name, new_address = tuple(new_device.values())
                self.logger.info(
                        f"Loaded device {new_name}: {new_address}"
                )

    # remove device from config dict and dict
    def remove_device(self, device_name):
        loop = asyncio.get_event_loop()
        disconnect_task = loop.create_task(
            self.clients[device_name].disconnect()
        )
        self.tasks.add(disconnect_task)
        disconnect_task.add_done_callback(self.tasks.discard)
        del self.clients[device_name]
        self.remove_device_from_conf(device_name)
        self.logger.info(f"Removing device {device_name}")

    async def disconnect_from_clients(self):
        self.logger.info(f"Disconnecting from all clients")
        for client in self.clients.values():
            await client.disconnect()

    @asyncClose
    async def closeEvent(self, a0) -> None:
        self.config_manager.save_config(self.config)
        await self.disconnect_from_clients()
