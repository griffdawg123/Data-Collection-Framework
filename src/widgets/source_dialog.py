from typing import Dict, Optional
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
        QButtonGroup,
        QCheckBox,
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QRadioButton,
        QSpinBox,
        QVBoxLayout,
        QWidget
)
from bleak import BleakClient

from src.ble.ble_scanner import get_services
from src.loaders.device_manager import DeviceManager

class BLESourceDialog(QDialog):
    # config is used if we are editing a source
    def __init__(self, config = {}):
        super().__init__()
        self.dm = DeviceManager()
        self.config = config

        # Source Name
        self.source_name_input = QLineEdit()
        self.source_name_input.setText(self.config.get("name", ""))

        # Client select
        self.client_select = QComboBox()
        self.client_select.addItems(self.dm.get_clients().keys())
        self.client_select.setCurrentText(self.config.get("name", ""))
        self.current_client = self.dm.get_clients().get(self.config.get("name", ""), None)
        if not self.current_client and len(self.dm.get_clients()) > 0:
            self.current_client = list(self.dm.get_clients().values())[0]
        self.client_select.currentTextChanged.connect(self.select_client)

        # Characteristic Select
        self.current_client_characteristics = {}
        self.characteristic_select = QComboBox()
        self.characteristic_select.addItem("--- not connected ---")
        if self.current_client and self.current_client.is_connected:
            self.characteristic_select.removeItem(0)
            self.characteristic_select.addItems(get_services(self.current_client).get("notify", {}).keys())
        self.characteristic_select.currentTextChanged.connect(self.set_characteristics)

        # UUID Input
        self.UUID_input = QLineEdit()
        self.UUID_input.setText(self.config.get("UUID", ""))
        if characteristic := self.config.get("characteristic"):
            self.characteristic_select.setCurrentText(characteristic)
        self.dm.connect_to_remove(self.update_client_select)
        self.dm.connect_to_add(self.update_client_select)

        # Encoding Select
        self.chunk_select = QFixedPointForm()
        for chunk in self.config.get("chunks", {}):
            self.chunk_select.add_chunk(False, chunk)

        # Dialog buttons
        self.dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.dialog_buttons.accepted.connect(self.accept)
        self.dialog_buttons.rejected.connect(self.reject)

        self.init_UI()

    def init_UI(self):
        layout = QFormLayout()
        layout.addRow(self.tr("Source Name: "), self.source_name_input)
        layout.addRow(self.tr("Client: "), self.client_select)
        layout.addRow(self.tr("Select Characteristic: "), self.characteristic_select)
        layout.addRow(self.tr("UUID: "), self.UUID_input)
        layout.addWidget(self.chunk_select)
        layout.addWidget(self.dialog_buttons)
        self.setLayout(layout)

    def select_client(self, client_name):
        self.current_client: Optional[ BleakClient ] = self.dm.get_clients().get(client_name, None)
        if self.current_client:
            self.current_client_characteristics = get_services(self.current_client)
        
    def set_characteristics(self, characteristic_name):
        if self.current_client == None:
            return
        self.UUID_input.setText(get_services(self.current_client).get("notify", {}).get(characteristic_name, ""))

    def update_client_select(self, _):
        for idx in range(self.client_select.count(), -1, -1):
            self.client_select.removeItem(idx)
        self.client_select.addItems(self.dm.get_clients().keys())

    def get_config(self):
        if not self.exec():
            return
        return {
            "name": self.source_name_input.text(),
            "client": self.client_select.currentText(),
            "characteristic": self.characteristic_select.currentText(),
            "UUID": self.UUID_input.text(),
            "chunks" : self.chunk_select.get_config()
        }

class QFixedPointForm(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.add_chunk_button = QPushButton("Add Chunk")
        self.remove_chunk_button = QPushButton("Remove Chunk")

        self.add_chunk_button.clicked.connect(self.add_chunk)
        self.remove_chunk_button.clicked.connect(self.remove_chunk)
        
        self.chunks = []
        self.init_UI()

    def init_UI(self):
        self.vbox = QVBoxLayout()
        buttons = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_chunk_button)
        buttons_layout.addWidget(self.remove_chunk_button)
        buttons.setLayout(buttons_layout)

        self.vbox.addWidget(buttons)
        self.setLayout(self.vbox)

    def get_config(self):
        return [ c.get_config() for c in self.chunks ]

    def add_chunk(self, _=False, chunk: Dict = {}):
        print("Chunk: ", chunk)
        new_chunk = QFixedPointChunk(chunk)
        self.vbox.insertWidget(len(self.chunks), new_chunk)
        self.chunks.append(new_chunk)

    def remove_chunk(self):
        if len(self.chunks) == 0:
            return
        to_remove = self.chunks.pop()
        self.vbox.removeWidget(to_remove)
        self.updateGeometry()

class QFixedPointChunk(QWidget):
    def __init__(self, chunk: Dict = {}) -> None:
        super().__init__()
        self.fixed_point_button = QRadioButton("Fixed Point (mQn)")
        self.fixed_point_button.setChecked(chunk.get("type", "fixed") == "fixed")
        self.floating_point_button = QRadioButton("Floating Point (float)")
        self.floating_point_button.setChecked(chunk.get("type", "fixed") == "float")
        self.button_box = QButtonGroup()
        self.button_box.addButton(self.fixed_point_button)
        self.button_box.addButton(self.floating_point_button)
        self.button_box.buttonClicked.connect(self.set_type)
        self.length = QSpinBox()
        self.length.setRange(0, 512*8)
        self.length.setSingleStep(2)
        self.length.setValue(chunk.get("length", 0))
        self.remainder = QSpinBox()
        self.remainder.setRange(0, 512*8)
        self.remainder.setValue(chunk.get("remainder", 0))
        self.signed = QCheckBox()
        self.signed.setChecked(chunk.get("signed", False))
        self.init_UI()

    def init_UI(self):
        layout = QFormLayout()
        layout.addRow(self.fixed_point_button, self.floating_point_button)
        layout.addRow(self.tr("Length of Chunk (in bytes)"), self.length)
        layout.addRow(self.tr("Number of Remainder bits (0 if int)"), self.remainder)
        layout.addRow(self.tr("Signed?"), self.signed)

        self.setLayout(layout)

    def set_type(self):
        if self.floating_point_button.isChecked():
            self.length.setDisabled(True)
            self.remainder.setDisabled(True)
            self.signed.setDisabled(True)
        else:
            self.length.setDisabled(False)
            self.remainder.setDisabled(False)
            self.signed.setDisabled(False)
            
    def get_config(self):
        return {
            "length" : self.length.value(),
            "remainder" : self.remainder.value(),
            "signed" : self.signed.isChecked(),
            "type" : "fixed" if self.fixed_point_button.isChecked() else "float",
                }
