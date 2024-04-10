
from enum import IntEnum
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLineEdit, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup, QCheckBox, QComboBox
import sys

class BLEDataType(IntEnum):
    READ = 0
    NOTIFY = 1

#TODO allow for multiparsed inputs
#TODO allow for multiple graphs

class PlotWidget(QWidget):
    def __init__(self, uuid: str = "", data_type: BLEDataType = BLEDataType.READ, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.uuid = uuid
        self.data_type = data_type
        self.setObjectName("PlotWidget")

        self.plot = QWidget()
        self.settings_widget = QWidget()
        self.uuid_input = QLineEdit()
        self.data_type_widget = QWidget()
        self.signed_checkbox = QCheckBox("Signed?")
        self.num_bits = QWidget()
        self.bit_encoding = QWidget()
        self.init_uuid_input()
        self.init_data_type()
        self.init_num_bits()
        self.init_ui()

    def set_data_type(self, value):
        self.data_type = value
        print("setting")

    def init_ui(self):
        vbox = QVBoxLayout()
        settings_layout = QHBoxLayout()
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
    
    


if __name__=="__main__":
    app = QApplication(sys.argv)
    plot = PlotWidget()
    sys.exit(app.exec())
