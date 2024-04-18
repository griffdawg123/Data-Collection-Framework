from enum import IntEnum
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLineEdit, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup, QCheckBox, QComboBox, QPushButton, QSizePolicy
import sys

from bleak import BleakClient

from src.widgets.data_plot import DataPlot
from src.ble.ble_generators import BLEThread

class BLEDataType(IntEnum):
    READ = 0
    NOTIFY = 1

#TODO allow for multiparsed inputs
#TODO allow for multiple graphs

class PlotWidget(QWidget):
    def __init__(self, device_list: dict[str, BleakClient], uuid: str = "", data_type: BLEDataType = BLEDataType.READ, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.device_list = device_list
        self.uuid = uuid
        self.data_type = data_type
        self.setObjectName("PlotWidget")

        self.data_thread = None
        self.plot = None
        self.settings_widget = QWidget()
        self.device_picker = QComboBox()
        self.uuid_input = QLineEdit()
        self.data_type_widget = QWidget()
        self.signed_checkbox = QCheckBox("Signed?")
        self.num_bits = QWidget()
        self.bit_encoding = QLineEdit()
        self.control_buttons = QWidget()
        self.init_device_picker()
        self.init_uuid_input()
        self.init_data_type()
        self.init_num_bits()
        self.init_bit_encoding()
        self.init_control_buttons()
        self.init_ui()

    def set_data_type(self, value):
        self.data_type = value
        print("setting")

    def init_ui(self):
        vbox = QVBoxLayout()
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(self.device_picker)
        settings_layout.addWidget(self.uuid_input)
        settings_layout.addWidget(self.data_type_widget)
        settings_layout.addWidget(self.signed_checkbox)
        settings_layout.addWidget(self.num_bits)
        settings_layout.addWidget(self.bit_encoding)
        settings_layout.addWidget(self.control_buttons)
        self.settings_widget.setLayout(settings_layout)
        vbox.addWidget(self.plot)
        vbox.addWidget(self.settings_widget)
        self.setLayout(vbox)
        self.setStyleSheet("QWidget#PlotWidget { border : 5px solid black; }")
        self.show()

    def init_device_picker(self):
        self.device_picker.addItems(self.device_list.keys())

    def init_uuid_input(self):
        self.uuid_input.setPlaceholderText("Enter UUID")

    def init_data_type(self):
        button_group = QButtonGroup()
        read = QRadioButton("Read")
        read.setChecked(True)
        notify = QRadioButton("Notify")
        button_group.addButton(read, id=BLEDataType.READ)
        button_group.addButton(notify, id=BLEDataType.NOTIFY)
        # button_group.idClicked.connect(print)
        button_group.idToggled.connect(self.set_data_type)

        layout = QHBoxLayout()
        layout.addWidget(read)
        layout.addWidget(notify)
        self.data_type_widget.setLayout(layout)

    def init_num_bits(self):
        label = QLabel("Number of Bits:")
        combobox = QComboBox()
        combobox.addItems(['8', '16', '32'])

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(combobox)
        self.num_bits.setLayout(layout)

    def init_bit_encoding(self):
        self.bit_encoding.setPlaceholderText("Enter bit encoding (optional)")

    def init_control_buttons(self):
        play_button = QPushButton(">")
        pause_button = QPushButton("||")
        layout = QHBoxLayout()
        layout.addWidget(play_button)
        layout.addWidget(pause_button)
        self.control_buttons.setLayout(layout)

if __name__=="__main__":
    app = QApplication(sys.argv)
    plot = PlotWidget({"name": "thingy", "address":"blahablha"})
    sys.exit(app.exec())
