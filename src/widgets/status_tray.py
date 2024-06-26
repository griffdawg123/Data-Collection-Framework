from typing import Dict
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from bleak import BleakClient
import asyncio

from src.loaders.device_manager import DeviceManager
from src.widgets.ble_status import BLEStatus


class StatusTray(QScrollArea):
    def __init__(self, remove_device) -> None:
    # def __init__(self, remove_device, clients: dict[str, BleakClient] = {}) -> None:
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.event_loop = asyncio.get_event_loop()
        self.scroll_widget = QWidget()
        # self.clients: dict[str, BleakClient] = clients
        self.dm: DeviceManager = DeviceManager()
        self.dm.connect_connected_callback(self.set_widget_status)
        self.remove_device_config = remove_device
        self.statuses: dict[str, BLEStatus] = {}
        self.vbox = QVBoxLayout()
        self.load_all_devices() # fills the statuses dict with BLEStatus objects
        self.fill_layout()

    def fill_layout(self):
        for status in self.statuses.values():
            print("status")
            self.vbox.addWidget(status, alignment=Qt.AlignmentFlag.AlignCenter)
        self.stretch = self.vbox.addStretch(1)
        self.set_layout_widget()

    def set_widget_status(self, name, connected):
        self.statuses[name].set_connected(connected)

    def load_all_devices(self):
        for label, client in self.dm.get_clients().items():
        # for label, client in self.clients.items():
            status = BLEStatus(label, client, self.remove_device, self.retry_device, parent=self)
            status.resize(self.width(), status.height())
            self.statuses[label] = status
        
    def remove_device(self, device_name):
        self.scroll_widget.layout()
        self.vbox.removeWidget(self.statuses[device_name])
        self.statuses[device_name].deleteLater()
        self.statuses.pop(device_name)
        self.remove_device_config(device_name)
        self.set_layout_widget()

    def set_clients(self):
        for name, client in self.dm.get_clients().items():
            self.add_device(name, client)

    # def set_clients(self, clients: Dict[str, BleakClient]):
    #     print(f"Clients: {clients}")
    #     for name, client in clients.items():
    #         self.add_device(name, client)
    #     self.clients = clients

    def add_device(self, device_name, device):
        new_status = BLEStatus(device_name, device, self.remove_device, self.retry_device, parent=self)
        self.statuses[device_name] = new_status
        self.vbox.insertWidget(self.vbox.count() -1 , new_status)
        self.set_layout_widget()

    def retry_device(self, device_name):
        self.dm.connect_client(device_name)

    def set_layout_widget(self):
        self.scroll_widget.setLayout(self.vbox)
        self.setWidget(self.scroll_widget)
        self.update()
    
    def set_remove_func(self, func):
        self.remove_device_config = func
