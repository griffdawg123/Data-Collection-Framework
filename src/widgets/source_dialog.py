from PyQt6.QtWidgets import QBoxLayout, QComboBox, QDialog, QLabel, QVBoxLayout

from src.loaders.device_manager import DeviceManager

class BLESourceDialog(QDialog):
    # config is used if we are editing a source
    def __init__(self, config = {}):
        super().__init__()
        self.dm = DeviceManager()
        self.config = config

        # TODO: Implement Read capabilities

        # Client select

        # Characteristic Select

        # UUID Input

        # Encoding Select

        self.init_UI()

    def init_UI(self):
        label = QLabel("Source Dialog")
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

        


# class BLESourceArgsForm(QWidget):
#     def __init__(self, config = {}) -> None:
#         super().__init__()
#         self.config = config
#         self.dm: DeviceManager = DeviceManager()
#         self.current_client = self.dm.get_clients().get(self.config.get("name", ""), None)
#         if not self.current_client and len(self.dm.get_clients()) > 0:
#             self.current_client = list(self.dm.get_clients().values())[0]
#         self.current_client_characteristics = {}
#         self.current_type = self.config.get("type", "read")
#         self.read = QRadioButton("Read")
#         self.read.setChecked(self.config.get("type", self.current_type) == "read")
#         self.notify = QRadioButton("Notify")
#         self.notify.setChecked(self.config.get("type", self.current_type) == "notify")
#         self.button_group = QButtonGroup()
#         self.button_group.addButton(self.read)
#         self.button_group.addButton(self.notify)
#         self.button_group.buttonClicked.connect(self.select_type)
#         self.client_select = QComboBox()
#         self.client_select.addItems(self.dm.get_clients().keys())
#         self.client_select.setCurrentText(self.config.get("name", ""))
#         self.client_select.currentTextChanged.connect(self.select_client)
#         self.characteristic = QComboBox()
#         self.characteristic.addItem("--- not connected ---")
#         print("Current client: ", self.current_client)
#         if self.current_client and self.current_client.is_connected:
#             self.characteristic.removeItem(0)
#             self.characteristic.addItems(get_services(self.current_client).get(self.current_type, {}).keys())
#         self.characteristic.currentTextChanged.connect(self.set_characteristics)
#         self.UUID_input = QLineEdit()
#         self.UUID_input.setText(self.config.get("UUID", ""))
#         if self.config.get("characteristic"):
#             self.characteristic.setCurrentText(self.config.get("characteristic"))
#         self.dm.connect_to_remove(self.update_client_select)
#         self.dm.connect_to_add(self.update_client_select)
#         self.init_UI()

#     def init_UI(self):
#         layout = QFormLayout()
#         layout.addRow(self.read, self.notify)
#         layout.addRow(self.tr("Client: "), self.client_select)
#         layout.addRow(self.tr("Characteristic: "), self.characteristic)
#         layout.addRow(self.tr("UUID: "), self.UUID_input)
#         self.setLayout(layout)
    
#     def select_type(self, button):
#         if button.text() == self.read.text():
#             self.current_type = "read"
#         elif button.text() == self.notify.text():
#             self.current_type = "notify"
#         for idx in range(self.characteristic.count(), -1, -1):
#             self.characteristic.removeItem(idx)
#         if self.current_client:
#             self.characteristic.addItems(get_services(self.current_client).get(self.current_type, {}).keys())
        
#     def select_client(self, client_name):
#         self.current_client: Optional[ BleakClient ] = self.dm.get_clients().get(client_name, None)
#         if self.current_client:
#             self.current_client_characteristics = get_services(self.current_client)
#             print(self.current_client.address)
#             print( self.current_client_characteristics )

#     def set_characteristics(self, characteristic_name):
#         if self.current_client == None:
#             return
#         self.UUID_input.setText(get_services(self.current_client).get(self.current_type, {}).get(characteristic_name, ""))

#     def update_client_select(self, _):
#         for idx in range(self.client_select.count(), -1, -1):
#             self.client_select.removeItem(idx)
#         self.client_select.addItems(self.dm.get_clients().keys())

#     def get_config(self):
#         return {
#             "name": self.client_select.currentText(),
#             "UUID": self.UUID_input.text(),
#             "characteristic": self.characteristic.currentText(),
#             "type": self.current_type,
#                 }


# class QFixedPointForm(ParamForm):
#     def __init__(self) -> None:
#         super().__init__()
#         self.which_chunk = QSpinBox()
#         self.which_chunk.setMinimum(0)
#         self.which_chunk.setMaximum(0)
#         self.add_chunk_button = QPushButton("Add Chunk")
#         self.remove_chunk_button = QPushButton("Remove Chunk")

#         self.add_chunk_button.clicked.connect(self.add_chunk)
#         self.remove_chunk_button.clicked.connect(self.remove_chunk)
        
#         self.chunks = []
#         self.init_UI()

#     def init_UI(self):
#         self.vbox = QVBoxLayout()

#         which_chunk = QWidget()
#         which_chunk_layout = QHBoxLayout()
#         which_chunk_label = QLabel("Which Chunk: ")
#         which_chunk_layout.addWidget(which_chunk_label)
#         which_chunk_layout.addWidget(self.which_chunk)
#         which_chunk.setLayout(which_chunk_layout)
#         self.vbox.addWidget(which_chunk)
        
#         buttons = QWidget()
#         buttons_layout = QHBoxLayout()
#         buttons_layout.addWidget(self.add_chunk_button)
#         buttons_layout.addWidget(self.remove_chunk_button)
#         buttons.setLayout(buttons_layout)

#         self.vbox.addWidget(buttons)
#         self.setLayout(self.vbox)

#     def get_config(self):
#         return {
#                 "chunk" : self.which_chunk.value(),
#                 "chunks" : [ c.get_config() for c in self.chunks ]
#         }

#     def add_chunk(self, _=False, chunk: Dict = {}):
#         print("Chunk: ", chunk)
#         new_chunk = QFixedPointChunk(chunk)
#         self.vbox.insertWidget(len(self.chunks), new_chunk)
#         self.chunks.append(new_chunk)
#         self.which_chunk.setMaximum(len(self.chunks)-1)

#     def remove_chunk(self):
#         if len(self.chunks) == 0:
#             return
#         to_remove = self.chunks.pop()
#         self.vbox.removeWidget(to_remove)
#         self.updateGeometry()
#         self.which_chunk.setMaximum(len(self.chunks)-1)

#     def set_values(self, config):
#         self.which_chunk.setValue(config.get("chunk", 0))
#         for chunk in config.get("chunks", []):
#             self.add_chunk(chunk=chunk)

# class QFixedPointChunk(ParamForm):
#     def __init__(self, chunk: Dict = {}) -> None:
#         super().__init__()
#         self.length = QSpinBox()
#         self.length.setRange(0, 512*8)
#         self.length.setSingleStep(2)
#         self.length.setValue(chunk.get("length", 0))
#         self.remainder = QSpinBox()
#         self.remainder.setRange(0, 512*8)
#         self.remainder.setValue(chunk.get("remainder", 0))
#         self.signed = QCheckBox()
#         self.signed.setChecked(chunk.get("signed", False))
#         self.init_UI()

#     def init_UI(self):
#         layout = QFormLayout()
#         layout.addRow(self.tr("Length of Chunk (in bytes)"), self.length)
#         layout.addRow(self.tr("Number of Remainder bits (n in m Q n)"), self.remainder)
#         layout.addRow(self.tr("Signed?"), self.signed)

#         self.setLayout(layout)
            
#     def get_config(self):
#         return {
#             "length" : self.length.value(),
#             "remainder" : self.remainder.value(),
#             "signed" : self.signed.isChecked(),
#                 }
