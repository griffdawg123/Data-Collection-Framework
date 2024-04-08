from typing import List
from PyQt6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt
from qasync import QEventLoop
from bleak import BleakClient
import asyncio
import sys

from src.widgets.ble_status import BLEStatus


class StatusTray(QScrollArea):
    def __init__(self, clients: dict[str, BleakClient]) -> None:
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.clients = clients
        self.fill_layout()

    def fill_layout(self):
        self.vbox = QVBoxLayout()
        # self.vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for label, client in self.clients.items():
            status = BLEStatus(label, client, self.remove_device, parent=self)
            status.resize(self.width(), status.height())
            self.vbox.addWidget(status, alignment=Qt.AlignmentFlag.AlignCenter)
        self.vbox.addStretch(1)
        self.scroll_widget.setLayout(self.vbox)
        self.setWidget(self.scroll_widget)
        
    def remove_device(self, device_name):
        print(device_name)

if __name__=="__main__":

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    devices = {"THINGY" : BleakClient("F1:EC:95:17:0A:62"), "THONGY" : BleakClient("F1:EC:95:17:0A:63")}
    scroll = StatusTray(devices)
    scroll.setGeometry(200, 200, 100, 100)
    scroll.show()
    loop.run_forever()