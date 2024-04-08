import asyncio
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt
import sys
from qasync import QEventLoop
from bleak import BleakClient

from src.widgets.led_indicator import LEDColor, LEDIndicator

class BLEStatus(QWidget):

    def __init__(self, device_label: str, device: BleakClient, remove_func, parent=None) -> None:
        super().__init__(parent)
        self.label = device_label
        self.client = device
        self.address = self.client.address
        self.title_label = QLabel(self.label)
        self.current_status = LEDColor.IDLE
        self.stat_led = LEDIndicator(self.current_status)
        self.stat_label = QLabel(self.current_status.name)
        self.retry = QPushButton()
        self.address_label = QLabel(self.address)
        self.remove_device = QPushButton("Remove")
        self.remove_device.clicked.connect(lambda _ : remove_func(self.label))
        self.init_ui()
        self.init_ble()

    def init_ui(self):
        layout = QVBoxLayout()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        layout.addWidget(self.address_label)

        self.indicator_widget = QWidget()
        indicator_layout = QHBoxLayout()
        indicator_layout.addWidget(self.stat_led)
        indicator_layout.addWidget(self.stat_label)
        self.indicator_widget.setLayout(indicator_layout)
        layout.addWidget(self.indicator_widget)
        self.retry.setText("Retry")
        self.retry.clicked.connect(self.init_ble)
        layout.addWidget(self.retry)
        layout.addWidget(self.remove_device)

        self.setLayout(layout)
        self.setStyleSheet("border: 1px solid black;")

    def init_ble(self):
        self.current_status = LEDColor.IDLE
        self._update()
        event_loop = asyncio.get_event_loop()
        connect_task = event_loop.create_task(self.client.connect())
        connect_task.add_done_callback(self.set_status)

    def set_status(self, task: asyncio.Task):
        exp = task.exception()
        if exp:
            print(exp)
            self.current_status = LEDColor.ERROR
        elif self.client.is_connected:
            print(f"Connected to device: {self.client.address}")
            self.current_status = LEDColor.OKAY
        else:
            print("Retry")
            self.current_status = LEDColor.IDLE
        self._update()

    def _update(self):
        self.stat_label.setText(self.current_status.name)
        self.stat_led.set_status(self.current_status)
        self.update()



if __name__=="__main__":

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    device = BleakClient("F1:EC:95:17:0A:62")
    status = BLEStatus("THINGY", device, print)
    status.setGeometry(200, 200, 100, 100)
    status.show()
    loop.run_forever()