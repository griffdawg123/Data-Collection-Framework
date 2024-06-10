
#         {
#             "title" : "Sin Plot",
#             "sources" : [
#                 {

#                     "type" : "time",
#                     "func" : {
#                         "name" : "sin",
#                         "params" : {
#                             "a" : 1,
#                             "b" : 1,
#                             "c" : 0,
#                             "d" : 0,
#                         },
#                     },
#                     "pen_colour" : "FFFF00",
#                     "source_name" : "sin"
#                 }
#             ],
#             "num_data_points" : 100,
#             "y_max" : 1,
#             "y_min" : -1,
#             "x_label" : "Time",
#             "x_units" : "s",
#             "y_label" : "Value",
#             "y_units" : ""
#         }

from abc import abstractmethod
import functools
from typing import Dict
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QColorDialog,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QSpinBox,
        QStackedWidget,
        QVBoxLayout,
        QWidget
        )

class ConfigForm(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.title = QLineEdit()
        self.new_source_button = QPushButton("Add Source")
        self.new_source_button.clicked.connect(self.add_source)
        self.new_source_name = QLineEdit("My Source")
        self.remove_source_button = QPushButton("Remove Source")
        self.remove_source_button.clicked.connect(self.remove_source)
        self.source_map = {}
        self.sources = QComboBox()
        self.sources.currentTextChanged.connect(self.change_source)
        self.source_stack = QStackedWidget()
        self.data_points = QSpinBox()
        self.y_max = QDoubleSpinBox()
        self.y_min = QDoubleSpinBox()
        self.x_label = QLineEdit()
        self.x_units = QLineEdit()
        self.y_label = QLineEdit()
        self.y_units = QLineEdit()
        
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
        layout.addRow(self.new_source_button, self.new_source_name)
        layout.addRow(self.remove_source_button, self.sources)
        layout.addWidget(self.source_stack)


        self.get_config_button = QPushButton("Get Config")
        self.get_config_button.clicked.connect(lambda _: print(self.get_config()))
        layout.addWidget(self.get_config_button)

        self.setLayout(layout)
        self.show()

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

    def add_source(self):
        text = self.new_source_name.text()
        if text == "" or text in self.source_map.keys():
            return
        source_form = SourceForm(text)
        self.source_map[self.new_source_name.text()] = source_form
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
    def __init__(self, name = "") -> None:
        super().__init__()
        self.name = QLineEdit(name)
        self.available_sources = {
            "BLE Device" : "ble",
            "Internal Clock" : "time",
                }
        self.source_type = QComboBox()
        self.source_type.addItems(self.available_sources.keys())
        self.pen_color = QPushButton("Choose Color")
        self.pen_color_dialog = QColorDialog()
        self.pen_color.clicked.connect(self.pen_color_dialog.open)
        self.pen_color_input = QLineEdit()
        self.pen_color_dialog.currentColorChanged.connect(self.set_color_text)
        self.args = QWidget() # TODO: Implement BLE args with client after
        self.func = FuncForm()
        self.init_UI()

    def init_UI(self):
        layout = QFormLayout()
        layout.addRow(self.tr("Source name: "), self.name)
        layout.addRow(self.tr("Source type: "), self.source_type)
        layout.addRow(self.pen_color, self.pen_color_input)
        layout.addRow(QLabel("Function: "), self.func)


        self.setLayout(layout)
        self.show()

    def get_config(self):
        return {
            "type": self.available_sources.get(self.source_type.currentText(), ''),
            "source_name": self.name.text(),
            "pen_color": self.pen_color_input.text(),
            "func" : self.func.get_config(),
        }

    def set_color_text(self, color: QColor):
        self.pen_color_input.setText(color.name())

class FuncForm(QWidget):

    def __init__(self) -> None:
        super().__init__()
        self.form = QFormLayout()
        self.func_type = QComboBox()
        self.available_funcs: Dict[str, ParamForm] = {
                "Sin: asin(bx+c)+d": TrigForm(),
                "Cos: acos(bx+c)+d": TrigForm(),
                "Q Fixed-Point: mQn encoding": QFixedPointForm(),
                "Identity: No Func": ParamForm(),
                }

        self.internal_names = {
            "Sin: asin(bx+c)+d" : "sin",
            "Cos: acos(bx+c)+d" : "cos",
            "Q Fixed-Point: mQn encoding" : "fixed_point",
            "Identity: No Func" : "identity",
        }
        self.func_type.addItems(self.available_funcs.keys())
        self.func_type.currentTextChanged.connect(self.update_param_form)
        self.param_form: QStackedWidget = QStackedWidget()
        for w in self.available_funcs.values():
            self.param_form.addWidget(w)
        self.init_UI()

    def init_UI(self):
        self.form.addRow(self.tr("Function Type"), self.func_type)
        self.form.addWidget(self.param_form)
        

        self.setLayout(self.form)
        self.show()

    def update_param_form(self):
        self.param_form.setCurrentWidget(self.available_funcs.get(self.func_type.currentText()))
        self.update()

    def get_config(self):
        current_widget = self.param_form.currentWidget()
        params = {}
        if current_widget and issubclass(type(current_widget), ParamForm):
            params = current_widget.get_config()

        return {
            "type" : self.internal_names.get(self.func_type.currentText()),
            "params" : params
        }

class ParamForm(QWidget):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def init_UI(self):
        return

    @abstractmethod
    def get_config(self):
        return {}

class TrigForm(ParamForm):
    def __init__(self) -> None:
        super().__init__()
        self.a = QDoubleSpinBox()
        self.b = QDoubleSpinBox()
        self.c = QDoubleSpinBox()
        self.d = QDoubleSpinBox()
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

    def add_chunk(self):
        new_chunk = QFixedPointChunk()
        self.vbox.insertWidget(len(self.chunks), new_chunk)
        self.chunks.append(new_chunk)

    def remove_chunk(self):
        if len(self.chunks) == 0:
            return
        to_remove = self.chunks.pop()
        self.vbox.removeWidget(to_remove)
        self.updateGeometry()

class QFixedPointChunk(ParamForm):
    def __init__(self) -> None:
        super().__init__()
        self.length = QSpinBox()
        self.remainder = QSpinBox()
        self.signed = QCheckBox()
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


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    ff = ConfigForm()
    sys.exit(app.exec())
    
        
