from enum import Enum
from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QLabel

class LEDColor(Enum):
    IDLE = "green"
    OKAY = "lightgreen"
    ERROR = "red"

class LEDIndicator(QLabel):

    def __init__(self, colour, radius=10) -> None:
        super().__init__()
        self.colour = colour
        self.radius = radius
        self.init_ui()
    
    def init_ui(self):
        self.setText("")
        self.resize(self.radius, self.radius)
        self._update()

    def set_status(self, status: LEDColor):
        self.colour = status
        self._update()

    def resizeEvent(self, event) -> None:
        self.resize(self.radius, self.radius)

    def _update(self):
        self.setStyleSheet(f"border-radius : {self.radius // 2}; border : 1px solid black; background-color : {self.colour.value}")
        self.update()

    