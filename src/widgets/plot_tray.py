from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtCore import Qt

class PlotTray(QScrollArea):
    def __init__(self) -> None:
        super().__init__()
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
