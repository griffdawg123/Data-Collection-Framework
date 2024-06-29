from abc import abstractmethod
from enum import Enum, IntEnum
import functools
import sys
from typing import Dict, List, Optional, Tuple
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
        QButtonGroup,
        QCheckBox,
        QColorDialog,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLineEdit,
        QPushButton,
        QRadioButton,
        QSpinBox,
        QStackedWidget,
        QVBoxLayout,
        QWidget
        )
from bleak import BleakClient

from src.ble.ble_scanner import get_services
from src.loaders.device_manager import DeviceManager

class ConfigForm(QWidget):
    def __init__(self, config = {}, clients = {}) -> None:
        super().__init__()
        self.title = QLineEdit()
        self.title.setText(config.get("title", ""))
        # self.clients = clients
        self.new_source_name_edit = QLineEdit()
        self.new_source_name_edit.textChanged.connect(
                lambda s: self.new_source_button.setDisabled(
                    len(s) == 0
                )
            )
        self.new_source_name = ""
        def set_source_name(s):
            self.new_source_name = s
            print(self.new_source_name)
        self.new_source_name_edit.textChanged.connect(set_source_name)        


        def new_source_clicked():
            self.add_source({"source_name": self.new_source_name})
        self.new_source_button = QPushButton("Add Source")
        self.new_source_button.clicked.connect(new_source_clicked)
        self.new_source_button.setDisabled(True)
        self.remove_source_button = QPushButton("Remove Source")
        self.remove_source_button.clicked.connect(self.remove_source)
        self.source_map = {}
        self.sources = QComboBox()
        self.source_stack = QStackedWidget()

        self.data_points = QSpinBox()
        self.data_points.setRange(1, 250)
        self.data_points.setValue(config.get("num_data_points", 1))

        self.y_max = QDoubleSpinBox()
        self.y_max.setRange(float('-inf'), float('inf'))
        self.y_max.setValue(config.get("y_max", 0))
        self.y_min = QDoubleSpinBox()
        self.y_min.setRange(float('-inf'), float('inf'))
        self.y_min.setValue(config.get("y_min", 0))

        self.x_label = QLineEdit()
        self.x_label.setText(config.get("x_label",""))
        self.x_units = QLineEdit()
        self.x_units.setText(config.get("x_units",""))
        self.y_label = QLineEdit()
        self.y_label.setText(config.get("y_label",""))
        self.y_units = QLineEdit()
        self.y_units.setText(config.get("y_units",""))
        
        self.init_UI()
        for source in config.get("sources", []):
            self.add_source(source)
        self.sources.currentTextChanged.connect(self.change_source)

    def init_UI(self):
        layout = QFormLayout()
        layout.addRow(self.tr("Plot Title"), self.title)
        layout.addRow(self.tr("Number of data points (x axis)"), self.data_points)
        layout.addRow(self.tr("Y max value"), self.y_max)
        layout.addRow(self.tr("Y min value"), self.y_min)
        layout.addRow(self.tr("X axis label"), self.x_label)
        layout.addRow(self.tr("X axis units"), self.x_units)
        layout.addRow(self.tr("Y axis label"), self.y_label)
        layout.addRow(self.tr("Y axis units"), self.y_units)
        layout.addRow(self.new_source_button, self.new_source_name_edit)
        layout.addRow(self.remove_source_button, self.sources)
        layout.addWidget(self.source_stack)
        self.setLayout(layout)

    def get_config(self):
        return {
                "title" : self.title.text(),
                "num_data_points" : self.data_points.value(),
                "y_max" : self.y_max.value(),
                "y_min" : self.y_min.value(),
                "x_label" : self.x_label.text(),
                "x_units" : self.x_units.text(),
                "y_label" : self.y_label.text(),
                "x_label" : self.x_label.text(),
                "sources" : [ s.get_config() for s in self.source_map.values() ]
        }

    def add_source(self, source = {}):
        text = source.get("source_name", "")
        if text == "" or text in self.source_map.keys():
            return
        source_form = SourceForm(source)
        self.source_map[self.new_source_name] = source_form
        self.sources.addItem(text)
        self.sources.setCurrentText(text)
        self.source_stack.addWidget(source_form)
        self.source_stack.setCurrentWidget(source_form)

    def remove_source(self):
        if len(self.source_map) == 0:
            return
        to_remove = self.source_map[self.sources.currentText()]
        self.source_stack.removeWidget(to_remove)
        del self.source_map[self.sources.currentText()]
        
    def change_source(self):
        self.source_stack.setCurrentWidget(self.source_map[self.sources.currentText()])

class SourceForm(QWidget):
    def __init__(self, config = {}) -> None:
        super().__init__()
        self.name = QLineEdit()
        source_name: Optional[str] = config.get("source_name", None)
        self.name.setText(source_name)
        self.available_sources = {
            "BLE Device" : "ble",
            "Internal Clock" : "time",
        }
        self.source_type = QComboBox()
        source_keys = list(self.available_sources.keys())
        source_values = list(self.available_sources.values())
        self.args = BLESourceArgsForm(config.get("args", {}))
        self.source_type.addItems(source_keys)
        self.source_type.setCurrentIndex(source_values.index(config.get("type","ble"))) 
        self.source_type.currentIndexChanged.connect(lambda idx: self.args.show() if idx == 0 else self.args.hide())
        self.pen_color = QPushButton("Choose Color")
        self.pen_color_dialog = QColorDialog()
        self.pen_color.clicked.connect(self.pen_color_dialog.open)
        self.pen_color_input = QLineEdit()
        self.pen_color_input.setText(config.get("pen_color", ""))
        self.pen_color_dialog.currentColorChanged.connect(self.set_color_text)
        self.func = FuncForm(config.get("func", {}))
        self.init_UI()

    def init_UI(self):
        layout = QFormLayout()
        layout.addRow(self.tr("Source name: "), self.name)
        layout.addRow(self.tr("Source type: "), self.source_type)
        layout.addWidget(self.args)
        layout.addRow(self.pen_color, self.pen_color_input)
        layout.addRow(QLabel("Function: "), self.func)

        self.args.show() if self.source_type.currentIndex == 0 else self.args.hide()

        self.setLayout(layout)
        self.show()

    def get_config(self):
        return {
            "type": self.available_sources.get(self.source_type.currentText(), ''),
            "source_name": self.name.text(),
            "pen_color": self.pen_color_input.text(),
            "func" : self.func.get_config(),
            "args" : self.args.get_config(),
        }

    def set_color_text(self, color: QColor):
        self.pen_color_input.setText(color.name())

class BLESourceArgsForm(QWidget):
    def __init__(self, config = {}, clients = {}) -> None:
        super().__init__()
        self.config = config
        self.dm: DeviceManager = DeviceManager()
        self.current_client = self.dm.get_clients().get(self.config.get("name", ""), None)
        if not self.current_client and len(self.dm.get_clients()) > 0:
            self.current_client = list(self.dm.get_clients().values())[0]
        self.current_client_characteristics = {}
        self.current_type = "read"
        self.read = QRadioButton("Read")
        self.read.setChecked(self.config.get("type", self.current_type) == "read")
        self.notify = QRadioButton("Notify")
        self.notify.setChecked(self.config.get("type", self.current_type) == "notify")
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.read)
        self.button_group.addButton(self.notify)
        self.button_group.buttonClicked.connect(self.select_type)
        self.client_select = QComboBox()
        self.client_select.addItems(self.dm.get_clients().keys())
        self.client_select.setCurrentText(self.config.get("name", ""))
        self.client_select.currentTextChanged.connect(self.select_client)
        self.characteristic = QComboBox()
        self.characteristic.addItem("--- not connected ---")
        print("Current client: ", self.current_client)
        if self.current_client and self.current_client.is_connected:
            self.characteristic.removeItem(0)
            self.characteristic.addItems(get_services(self.current_client).get(self.current_type, {}).keys())
        self.characteristic.currentTextChanged.connect(self.set_characteristics)
        self.UUID_input = QLineEdit()
        self.UUID_input.setText(self.config.get("UUID", ""))
        self.dm.connect_to_remove(self.update_client_select)
        self.dm.connect_to_add(self.update_client_select)
        self.init_UI()

    def init_UI(self):
        layout = QFormLayout()
        layout.addRow(self.read, self.notify)
        layout.addRow(self.tr("Client: "), self.client_select)
        layout.addRow(self.tr("Characteristic: "), self.characteristic)
        layout.addRow(self.tr("UUID: "), self.UUID_input)
        self.setLayout(layout)
        self.show()
    
    def select_type(self, button):
        if button.text() == self.read.text():
            self.current_type = "read"
        elif button.text() == self.notify.text():
            self.current_type = "notify"
        for idx in range(self.characteristic.count(), -1, -1):
            self.characteristic.removeItem(idx)
        if self.current_client:
            self.characteristic.addItems(get_services(self.current_client).get(self.current_type, {}).keys())
        
    def select_client(self, client_name):
        # self.current_client: Optional[ BleakClient ] = self.clients.get(client_name, None)
        self.current_client: Optional[ BleakClient ] = self.dm.get_clients().get(client_name, None)
        if self.current_client:
            self.current_client_characteristics = get_services(self.current_client)
            print(self.current_client.address)
            print( self.current_client_characteristics )

    def set_characteristics(self, characteristic_name):
        if self.current_client == None:
            return
        self.UUID_input.setText(get_services(self.current_client).get(self.current_type, {}).get(characteristic_name, ""))

    def update_client_select(self, _):
        for idx in range(self.client_select.count(), -1, -1):
            self.client_select.removeItem(idx)
        self.client_select.addItems(self.dm.get_clients().keys())

    # def set_clients(self, clients):
    #     self.clients = clients
    #     for idx in range(self.client_select.count(), -1, -1):
    #         self.client_select.removeItem(idx)
    #     self.client_select.addItems(self.clients)

    def get_config(self):
        return {
            "name": self.client_select.currentText(),
            "UUID": self.UUID_input.text(),
            "type": self.current_type,
                }

class FuncInfo(IntEnum):
    LABEL = 0
    ID = 1
    FORM = 2

class FuncForm(QWidget):

    

    def __init__(self, config = {}) -> None:
        super().__init__()
        print(config)
        self.form = QFormLayout()
        self.func_type = QComboBox()
        self.funcs = [
            ("Sin: asin(bx+c)+d", "sin", TrigForm()),
            ("Cos: acos(bx+c)+d", "cos", TrigForm()),
            ("Q Fixed-Point: mQn encoding", "fixed_point", QFixedPointForm()),
            ("Identity: No Func", "identity", ParamForm()),
        ]
        self.func_type.addItems([func[FuncInfo.LABEL] for func in self.funcs])
        self.param_form: QStackedWidget = QStackedWidget()
        for w in [func[FuncInfo.FORM] for func in self.funcs]:
            self.param_form.addWidget(w)
        self.param_form.setCurrentIndex(
                [func[FuncInfo.ID] for func in self.funcs].index(config.get("type", "sin"))
        )
        self.funcs[self.param_form.currentIndex()][FuncInfo.FORM].set_values(config.get("params", {}))
        self.func_type.currentTextChanged.connect(self.update_param_form)
        self.init_UI()

    def init_UI(self):
        self.form.addRow(self.tr("Function Type"), self.func_type)
        self.form.addWidget(self.param_form)

        self.setLayout(self.form)
        self.show()

    def update_param_form(self):
        self.param_form.setCurrentIndex(self.func_type.currentIndex())
        self.update()

    def get_config(self):
        current_idx = self.param_form.currentIndex()
        params = self.funcs[current_idx][FuncInfo.FORM].get_config()
        return {
            "type" : self.funcs[self.param_form.currentIndex()][FuncInfo.ID],
            "params" : params
        }

class ParamForm(QWidget):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def init_UI(self):
        pass

    @abstractmethod
    def get_config(self):
        return {}

    @abstractmethod
    def set_values(self, config):
        pass

class TrigForm(ParamForm):
    def __init__(self) -> None:
        super().__init__()
        self.a = QDoubleSpinBox()
        self.a.setRange(sys.float_info.min, sys.float_info.max)
        self.b = QDoubleSpinBox()
        self.b.setRange(sys.float_info.min, sys.float_info.max)
        self.c = QDoubleSpinBox()
        self.c.setRange(sys.float_info.min, sys.float_info.max)
        self.d = QDoubleSpinBox()
        self.d.setRange(sys.float_info.min, sys.float_info.max)
        self.init_UI()

    def init_UI(self):
        layout = QFormLayout()
        layout.addRow(self.tr("a"), self.a)
        layout.addRow(self.tr("b"), self.b)
        layout.addRow(self.tr("c"), self.c)
        layout.addRow(self.tr("d"), self.d)
        self.setLayout(layout)

    def get_config(self):
        return {
            "a" : self.a.value(),
            "b" : self.b.value(),
            "c" : self.c.value(),
            "d" : self.d.value(),
                }
    
    def set_values(self, config):
        self.a.setValue(config.get("a", 0))
        self.b.setValue(config.get("b", 0))
        self.c.setValue(config.get("c", 0))
        self.d.setValue(config.get("d", 0))

class QFixedPointForm(ParamForm):
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
        return {"chunks" : [ c.get_config() for c in self.chunks ]}

    def add_chunk(self, checked = False, chunk: Dict = {}):
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

    def set_values(self, config):
        for chunk in config.get("chunks", []):
            self.add_chunk(chunk=chunk)

class QFixedPointChunk(ParamForm):
    def __init__(self, chunk: Dict = {}) -> None:
        super().__init__()
        self.length = QSpinBox()
        self.length.setRange(0, 512*8)
        self.length.setSingleStep(2)
        self.length.setValue(chunk.get("length", 0))
        self.remainder = QSpinBox()
        self.remainder.setRange(0, 512*8)
        self.remainder.setValue(chunk.get("remainder", 0))
        self.signed = QCheckBox()
        self.signed.setChecked(chunk.get("checked", False))
        self.init_UI()

    def init_UI(self):
        layout = QFormLayout()
        layout.addRow(self.tr("Length of Chunk (in bits)"), self.length)
        layout.addRow(self.tr("Number of Remainder bits (n in m Q n)"), self.remainder)
        layout.addRow(self.tr("Signed?"), self.signed)

        self.setLayout(layout)
            
    def get_config(self):
        return {
            "length" : self.length.value(),
            "remainder" : self.remainder.value(),
            "signed" : self.signed.isChecked(),
                }
