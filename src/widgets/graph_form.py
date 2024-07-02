from abc import abstractmethod
from enum import IntEnum
import json
import os
import sys
from typing import Dict, Optional
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
        QButtonGroup,
        QCheckBox,
        QColorDialog,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QHBoxLayout,
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

from src import helpers
from src.ble.ble_scanner import get_services
from src.loaders.config_loader import load_source, save_source
from src.loaders.device_manager import DeviceManager
from src.widgets import source_dialog
from src.widgets.source_dialog import BLESourceDialog

class ConfigForm(QWidget):
    def __init__(self, config = {}) -> None:
        super().__init__()

        # Plot Title
        self.title = QLineEdit()
        self.title.setText(config.get("title", "Untitled"))

        # New Plotline
        self.new_plotline_edit = QLineEdit()
        self.new_plotline_edit.textChanged.connect(
                lambda s: self.add_plotline_button.setDisabled(
                    len(s) == 0
                )
            )
        self.new_plotline_name = ""
        # self.new_source_combo = QComboBox()
        # self.available_sources = ["Time"] + [file_name.removesuffix(".config") for file_name in helpers.get_files("config/sources") ]
        # self.new_source_combo.addItems(self.available_sources)
        # self.new_source_combo.setLineEdit(self.new_source_name_edit)
        def set_plotline_name(s):
            self.new_plotline_name = s
        self.new_plotline_edit.textChanged.connect(set_plotline_name)        
        def new_plotline_button_clicked():
            self.add_plotline({"plotline_name": self.new_plotline_name})
        self.add_plotline_button = QPushButton("Add Plotline")
        self.add_plotline_button.clicked.connect(new_plotline_button_clicked)
        # self.new_source_button.setDisabled(True)
        self.remove_plotline_button = QPushButton("Remove Plotline")
        self.remove_plotline_button.clicked.connect(self.remove_plotline)
        self.plotline_forms = {}
        self.plotline_select = QComboBox()
        self.plotline_config_edit_stack = QStackedWidget()

        self.data_points = QSpinBox()
        self.data_points.setRange(1, 250)
        self.data_points.setValue(config.get("num_data_points", 100))

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

        # Add existing plots to the config
        for source in config.get("plotlines", []):
            self.add_plotline(source)
        self.plotline_select.currentTextChanged.connect(self.change_plotline)
        
        self.init_UI()

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
        layout.addRow(self.add_plotline_button, self.new_plotline_edit)
        layout.addRow(self.remove_plotline_button, self.plotline_select)
        layout.addWidget(self.plotline_config_edit_stack)
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
                "plotlines" : [ s.get_config() for s in self.plotline_forms.values() ]
        }

    def add_plotline(self, source = {}):
        # If we are trying to add a plot without a name
        text = source.get("plotline_name", "")
        if text == "" or text in self.plotline_forms.keys():
            return

        plotline_form = PlotlineForm(source)

        # Add new form to be tracked
        self.plotline_forms[text] = plotline_form
        self.plotline_select.addItem(text)
        self.plotline_select.setCurrentText(text)
        self.plotline_config_edit_stack.addWidget(plotline_form)
        self.plotline_config_edit_stack.setCurrentWidget(plotline_form)

    def remove_plotline(self):
        if len(self.plotline_forms) == 0:
            return
        to_remove = self.plotline_forms[self.plotline_select.currentText()]
        self.plotline_config_edit_stack.removeWidget(to_remove)
        del self.plotline_forms[self.plotline_select.currentText()]
        
    def change_plotline(self):
        print(self.plotline_forms)
        self.plotline_config_edit_stack.setCurrentWidget(self.plotline_forms[self.plotline_select.currentText()])

class PlotlineForm(QWidget):
    def __init__(self, config = {}) -> None:
        super().__init__()
        self.name = QLineEdit()

        # Plotline Name

        plotline_name: Optional[str] = config.get("plotline_name", None)
        self.name.setText(plotline_name)

        # Source Select
        self.available_sources = ["Time"] + [file_name.removesuffix(".config") for file_name in helpers.get_files("config/sources")]
        self.source_select = QComboBox()
        self.source_select.addItems(self.available_sources)
        self.source_select.setCurrentIndex(self.available_sources.index(helpers.format_config_name(config.get("source", "Time"))))

        # Source chunk select
        self.source_chunk_select = QSpinBox()
        self.source_chunk_select.setMinimum(0)

        # Add/Edit Source
        self.source_add_button = QPushButton("Add New Source")
        self.source_edit_button = QPushButton("Edit Source")
        self.source_add_button.clicked.connect(self.add_source)
        self.source_edit_button.clicked.connect(self.edit_source)

        # Pen Color Select
        self.pen_color = QPushButton("Choose Color")
        self.pen_color_dialog = QColorDialog()
        self.pen_color.clicked.connect(self.pen_color_dialog.open)
        self.pen_color_input = QLineEdit()
        self.pen_color_input.setText(config.get("pen_color", ""))
        self.pen_color_dialog.currentColorChanged.connect(self.set_color_text)

        # Func Select
        self.func = FuncForm(config.get("func", {}))
        self.init_UI()

    def init_UI(self):
        layout = QFormLayout()
        layout.addRow(self.tr("Plotline name: "), self.name)
        layout.addRow(self.tr("Source: "), self.source_select)
        layout.addRow(self.tr("Source Chunk: "), self.source_chunk_select)
        layout.addRow(self.source_add_button, self.source_edit_button)
        layout.addRow(self.pen_color, self.pen_color_input)
        layout.addRow(QLabel("Function: "), self.func)

        self.setLayout(layout)
        self.show()

    def get_config(self):
        return {
            "source": self.source_select.currentText(),
            "plotline_name": self.name.text(),
            "pen_color": self.pen_color_input.text(),
            "func" : self.func.get_config(),
            "chunk" : self.source_chunk_select.value(),
        }

    def set_color_text(self, color: QColor):
        self.pen_color_input.setText(color.name())

    def add_source(self):
        source_dialog = BLESourceDialog()
        source_dialog.hide()
        config = source_dialog.get_config()
        if not config:
            return
        self.set_source(config)

    def edit_source(self):
        source_dialog = BLESourceDialog(load_source(self.source_select.currentText()))
        config = source_dialog.get_config()
        if not config:
            return
        self.set_source(config)
        
    def set_source(self, config):
        # Save config to a new file
        print(config)
        save_source(config)
        # add new config to source selection box
        self.source_select.addItem(config["name"])
        # set current source to the new one
        self.source_select.setCurrentText(config["name"])


class FuncInfo(IntEnum):
    LABEL = 0
    ID = 1
    FORM = 2

class FuncForm(QWidget):
    def __init__(self, config = {}) -> None:
        super().__init__()
        self.form = QFormLayout()
        self.func_type = QComboBox()
        self.funcs = [
            ("Sin: asin(bx+c)+d", "sin", TrigForm()),
            ("Cos: acos(bx+c)+d", "cos", TrigForm()),
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

        self.func_type.setCurrentIndex(
                [func[FuncInfo.ID] for func in self.funcs].index(config.get("type", "sin"))
        )
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

