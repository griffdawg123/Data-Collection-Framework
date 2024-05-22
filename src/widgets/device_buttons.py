import sys
from typing import Callable
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget


class DeviceButtons(QWidget):
    def __init__(self, new_device: Callable, load_device: Callable, restart: Callable) -> None:
        super().__init__()
        self.new_device = QPushButton("New Device")
        self.load_device = QPushButton("Load Device")
        self.restart = QPushButton("Restart")

        self.new_device.clicked.connect(new_device)
        self.load_device.clicked.connect(load_device)
        self.restart.clicked.connect(restart)
        self.init_UI()

    def init_UI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.new_device)
        layout.addWidget(self.load_device)
        layout.addWidget(self.restart)
        self.setLayout(layout)

    def set_funcs(self, new, load, restart):
        self.new_device.clicked.connect(new)
        self.load_device.clicked.connect(load)
        self.restart.clicked.connect(restart)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = DeviceButtons(lambda: print("New"), lambda: print("Load"), lambda: print("restart"))
    db.show()
    sys.exit(app.exec())
