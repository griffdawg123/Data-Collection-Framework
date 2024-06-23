from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import sys

from bleak import BleakClient
from src.widgets.device_buttons import DeviceButtons
from src.widgets.status_tray import StatusTray
from src.widgets.control_buttons import ControlButtons

class Sidebar(QWidget):
    def __init__(
            self, 
            title: str = "", 
            remove_func: Callable = print,
            new_device: Callable = print,
            load_device: Callable = print,
            restart: Callable = print,
            edit_config: Callable = print,
            play: Callable = print,
            pause: Callable = print,
        ):
        super().__init__()
        self.header_text: QLabel = QLabel()
        self.status_tray: StatusTray = StatusTray(remove_func)
        self.device_buttons: DeviceButtons = DeviceButtons(new_device, load_device, restart, edit_config)
        self.control_buttons = ControlButtons()
        self.set_params(title, remove_func, new_device, load_device, restart, edit_config, {}, play, pause)
        self.init_UI()

    def set_params(self, title, remove, new, load, restart, edit_config, clients, play, pause):
        print(title)
        self.header_text.setText(title)
        self.header_text.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.status_tray.set_remove_func(remove)
        self.device_buttons.set_funcs(new, load, restart, edit_config)
        self.control_buttons.connect_funcs(play, pause)
        self.set_clients(clients)
        self.update()

    def set_clients(self, clients):
        self.clients = clients
        self.status_tray.set_clients(clients)

    def add_client(self, name, client):
        self.clients[name] = client
        self.status_tray.add_device(name, client)

    def init_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.header_text)
        layout.addWidget(self.control_buttons)
        layout.addWidget(self.status_tray)
        layout.addWidget(self.device_buttons)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    s = Sidebar()
    s.set_clients({"Hello": BleakClient("world")})
    s.show()
    sys.exit(app.exec())
