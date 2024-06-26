import logging
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QFileDialog
)
import json
from bleak import BleakClient
from qasync import asyncClose

from src import helpers
from src.loaders.config_loader import ConfigLoader
from src.loaders.device_manager import DeviceManager
from src.widgets.data_plot import Plots
from src.widgets.sidebar import Sidebar
from src.widgets.graph_config import GraphConfig
from src.windows.config_selection import ConfigSelection
from src.windows.new_device import NewDevice
from src.logs.logs_setup import LoggerEnv


class Workspace(QWidget):
    def __init__(self, log_level: LoggerEnv) -> None:
        super().__init__()
        
        # initialise values
        self.config_path: str = ""
        self.tasks = set()
        self.dm: DeviceManager = DeviceManager()

        # logger stup
        self.logger = logging.getLogger(log_level.value)
        self.logger.info("Logger Enabled")

        # setup config
        default_config = "src/loaders/default.config"
        self.config_manager = ConfigLoader(default_config, self.logger)
        self.config = self.config_manager.load_config()

        # setup inner widgets
        self.sidebar = Sidebar()
        self.config_window: ConfigSelection = ConfigSelection(
            self.logger,
            self.load_config
        )
        self.config_window.show()
        self.hide()
    
    # creates config manager
    def load_config(self, config_path: str) -> None:
        self.config_manager = ConfigLoader(config_path, self.logger)
        self.config = self.config_manager.load_config()
        self.load_devices_from_config()
        self.load_UI()
        self.showMaximized()

    def load_devices_from_config(self):
        self.dm.set_clients(self.config_manager.load_devices())
        self.config["devices"] = [helpers.format_config_name(name) for name in self.dm.get_client_names()]
        print(self.config["devices"])

    # initialises UI
    def load_UI(self) -> None:
        # Sidebar initialisation
        self.sidebar.set_params(
            self.config_manager.get_title(),
            self.remove_device,
            self.new_device,
            self.load_device,
            self.restart,
            self.edit_config,
            self.play,
            self.pause,
        )
        
        # Plot initialization
        self.plot_config = self.config.get("plots", {})
        self.plots = Plots(self.plot_config)

        # Layout setup
        self.workspace_layout: QHBoxLayout = QHBoxLayout()
        self.workspace_layout.addWidget(self.sidebar)
        self.workspace_layout.addWidget(self.plots)
        self.workspace_layout.setStretch(0, 1)
        self.workspace_layout.setStretch(1, 9)
        self.workspace = QWidget()
        self.workspace.setLayout(self.workspace_layout)
        self.setLayout(self.workspace_layout)
        self.logger.info("UI Loaded")

    def add_device(self, conf):
        client = BleakClient(conf["address"])
        self.dm.add_client(conf["name"], client)
        self.add_device_to_conf(conf["name"])
        self.sidebar.add_client(conf["name"], client)

    def add_device_to_conf(self, device_name):
        devices = self.config["devices"]
        devices.append(helpers.format_config_name(device_name))
        self.config["devices"] = devices
        self.config_manager.save_config(self.config)

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
                "address": address,
                "services": {}
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
        self.dm.remove_client(device_name)
        self.logger.info(f"Removing device {device_name}")

    def restart(self):
        self.plots.restart()

    def edit_config(self):
        self.config = self.config_manager.load_config()
        config_dialog = GraphConfig(self.config.get("plots", {}))
        config_dialog.hide()
        config = config_dialog.get_config()
        print(config)
        if not config:
            return
        self.config["plots"] = config
        self.config_manager.save_config(self.config)
        self.workspace_layout.removeWidget(self.plots)
        self.plots.stop()
        self.plots.close()
        self.plots = Plots(self.config["plots"])
        self.workspace_layout.addWidget(self.plots)
        self.workspace_layout.setStretch(0, 1)
        self.workspace_layout.setStretch(1, 9)

    def play(self):
        self.plots.start_clicked()

    def pause(self):
        self.plots.stop()

    async def disconnect_from_clients(self):
        self.logger.info(f"Disconnecting from all clients")
        await self.dm.disconnect_all()

    @asyncClose
    async def closeEvent(self, _) -> None: # pyright: ignore[reportIncompatibleMethodOverride]
        self.config_manager.save_config(self.config)
        await self.disconnect_from_clients()
