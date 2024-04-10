
from enum import Enum
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLineEdit, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton
import sys

class BLEDataType(Enum):
    READ = 0
    NOTIFY = 1

class PlotWidget(QWidget):
    def __init__(self, UUID: str = "", data_type: BLEDataType = BLEDataType.READ, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.plot = QWidget()
        self.settings_widget = QWidget()
        self.UUID_input = QLineEdit()
        self.data_type = data_type
        self.data_type_widget = QWidget()
        self.bit_encoding = QWidget()
        self.init_UUID_input()
        self.init_data_type()
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(self.UUID_input)
        settings_layout.addWidget(self.data_type_widget)
        settings_layout.addWidget(self.bit_encoding)
        self.settings_widget.setLayout(settings_layout)
        vbox.addWidget(self.plot)
        vbox.addWidget(self.settings_widget)
        self.setLayout(vbox)
        self.show()

    def init_UUID_input(self):
        self.UUID_input.setPlaceholderText("Enter UUID")

    def init_data_type(self):
        read = QRadioButton()
        read_label = QLabel("Read")
        notify = QRadioButton()
        notify_label = QLabel("Notify")
        layout = QHBoxLayout()
        layout.addWidget(read_label)
        layout.addWidget(read)
        layout.addWidget(notify_label)
        layout.addWidget(notify)
        self.data_type_widget.setLayout(layout)

if __name__=="__main__":
    app = QApplication(sys.argv)
    plot = PlotWidget()
    sys.exit(app.exec())
