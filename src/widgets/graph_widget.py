from enum import IntEnum
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
        QWidget,
        QLineEdit,
        QApplication,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QRadioButton,
        QButtonGroup,
        QCheckBox,
        QComboBox,
        QPushButton,
        )
import sys

from bleak import BleakClient

from src.widgets.data_plot import DataPlot
from src.ble.ble_generators import BLEThread, ReadThread, NotifyThread
from src.widgets.ble_datatype import BLEDataType

#TODO allow for multiparsed inputs
#TODO allow for multiple graphs

class PlotWidget(QWidget):
    def __init__(self, device_list: dict[str, BleakClient], uuid: str = "", data_type: BLEDataType = BLEDataType.READ, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.device_list = device_list
        self.uuid = uuid
        self.data_type: BLEDataType = data_type
        self.signed: bool = False
        self.setObjectName("PlotWidget")

        self.client: BleakClient = None
        self.data_thread = None
        self.plot = DataPlot()
        self.settings_widget = QWidget()
        self.device_picker = QComboBox()
        self.uuid_input = QLineEdit()
        self.data_type_widget = QWidget()
        self.signed_checkbox = QCheckBox("Signed?")
        self.num_bits = QWidget()
        self.bit_encoding = QLineEdit()
        self.init_device_picker()
        self.init_uuid_input()
        self.init_data_type()
        self.init_signed()
        self.init_num_bits()
        self.init_bit_encoding()
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(self.device_picker)
        settings_layout.addWidget(self.uuid_input)
        settings_layout.addWidget(self.data_type_widget)
        settings_layout.addWidget(self.signed_checkbox)
        settings_layout.addWidget(self.num_bits)
        settings_layout.addWidget(self.bit_encoding)
        self.settings_widget.setLayout(settings_layout)
        vbox.addWidget(self.plot)
        vbox.addWidget(self.settings_widget)
        self.setLayout(vbox)
        self.setStyleSheet("QWidget#PlotWidget { border : 5px solid black; }")
        self.show()

    def init_device_picker(self):
        if self.device_list:
            self.set_client(list(self.device_list.keys())[0])
        self.device_picker.addItems(self.device_list.keys())
        self.device_picker.currentTextChanged.connect(lambda client_name: self.set_client(client_name))

    def init_uuid_input(self):
        self.uuid_input.setPlaceholderText("Enter UUID")
        self.uuid_input.textChanged.connect(lambda UUID: self.set_UUID(UUID))

    def init_data_type(self):
        self.button_group = QButtonGroup()
        self.button_group.setExclusive(True)
        read = QRadioButton("Read")
        read.setChecked(True)
        notify = QRadioButton("Notify")
        self.button_group.addButton(read, id=BLEDataType.READ)
        self.button_group.addButton(notify, id=BLEDataType.NOTIFY)
        # button_group.idClicked.connect(print)
        self.button_group.buttonClicked.connect(self.set_data_type)

        layout = QHBoxLayout()
        layout.addWidget(read)
        layout.addWidget(notify)
        self.data_type_widget.setLayout(layout)

    def init_signed(self):
        self.signed_checkbox.stateChanged.connect(self.set_signed)

    def init_num_bits(self):
        label = QLabel("Number of Bits:")
        combobox = QComboBox()
        combobox.addItems(['8', '16', '32'])
        combobox.currentTextChanged.connect(self.set_num_bits)

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(combobox)
        self.num_bits.setLayout(layout)

    def init_bit_encoding(self):
        self.bit_encoding.setPlaceholderText("Enter bit encoding (optional)")
        self.bit_encoding.textChanged.connect(self.set_bit_encoding)

    def set_client(self, client_name):
        self.client = self.device_list[client_name]
        print(client_name)

    def set_UUID(self, UUID):
        self.UUID = UUID
        print(UUID)

    def set_signed(self, signed):
        self.signed = bool(signed)
        print(signed)

    def set_data_type(self, button):
        button_id = self.button_group.id(button)
        self.data_type = button_id
        print(button_id)

    def set_num_bits(self, num_bits):
        self.num_bits = int(num_bits)
        print(num_bits)

    def set_bit_encoding(self, bit_encoding):
        self.bit_encoding = bit_encoding
        print(bit_encoding)

    def start(self):
        print("Starting in grpah widget")
        self.plot.start()

    def stop(self):
        self.plot.stop()

    def set_plot_thread(self):
        thread = None
        if self.data_type == BLEDataType.READ:
            thread = ReadThread(self.client, self.UUID)
        elif self.data_type == BLEDataType.NOTIFY:
            thread = NotifyThread(self.client, self.UUID)
        self.plot.set_source(thread)
    
    def set_plot_params(self, datarate: int = 60, num_data_points: int = 100, y_max: int = 10, y_min: int = 10):
        print(f"setting params {datarate, num_data_points, y_max, y_min}")
        self.plot.set_params(datarate, num_data_points, y_max, y_min)




if __name__=="__main__":
    app = QApplication(sys.argv)
    plot = PlotWidget({"name": "thingy", "address":"blahablha"})
    sys.exit(app.exec())
