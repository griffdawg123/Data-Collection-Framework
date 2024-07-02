from typing import Optional
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QColorDialog, QComboBox, QFormLayout, QLabel, QLineEdit, QPushButton, QWidget

from src.widgets.graph_form import BLESourceArgsForm, FuncForm


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
        self.source_type.currentTextChanged.connect(lambda txt: self.args.show() if txt == "BLE Device" else self.args.hide())
        if self.source_type.currentText() == "BLE Device":
            self.args.show()
        else:
            self.args.hide()
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
