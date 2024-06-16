import sys
from typing import Callable
from PyQt6.QtWidgets import QApplication, QGridLayout, QPushButton, QVBoxLayout, QWidget


class DeviceButtons(QWidget):
    def __init__(self, new_device: Callable, load_device: Callable, restart: Callable, edit_conf: Callable) -> None:
        super().__init__()
        self.new_device = QPushButton("New Device")
        self.load_device = QPushButton("Load Device")
        self.restart = QPushButton("Restart Plots")
        self.edit_conf = QPushButton("Edit Config")

        self.new_device.clicked.connect(new_device)
        self.load_device.clicked.connect(load_device)
        self.restart.clicked.connect(restart)
        self.edit_conf.clicked.connect(edit_conf)
        self.init_UI()

    def init_UI(self):
        layout = QGridLayout()
        layout.addWidget(self.new_device, 0, 0)
        layout.addWidget(self.load_device, 0, 1)
        layout.addWidget(self.restart, 1, 0)
        layout.addWidget(self.edit_conf, 1, 1)
        self.setLayout(layout)

    def set_funcs(self, new, load, restart, edit_config):
        self.new_device.clicked.connect(new)
        self.load_device.clicked.connect(load)
        self.restart.clicked.connect(restart)
        self.edit_conf.clicked.connect(edit_config)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # db = DeviceButtons(lambda: print("New"), lambda: print("Load"), lambda: print("restart"))
    # db.show()
    sys.exit(app.exec())
