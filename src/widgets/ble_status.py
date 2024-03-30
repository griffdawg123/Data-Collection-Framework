from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton
import sys

from src.widgets.led_indicator import LEDColor, LEDIndicator

class BLEStatus(QWidget):
    def __init__(self, device_label: str) -> None:
        super().__init__()
        self.label = device_label
        self.init_ui()
        self.show()

    def init_ui(self):
        self._layout = QVBoxLayout()
        self.title_label = QLabel()
        self.title_label.setText(self.label)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._layout.addWidget(self.title_label)
        self.indicator_widget = QWidget()
        self.indicator_layout = QHBoxLayout()

        current_status = LEDColor.ERROR

        self.stat_led = LEDIndicator(current_status)
        self.indicator_layout.addWidget(self.stat_led)

        self.stat_label = QLabel(current_status.name)
        self.indicator_layout.addWidget(self.stat_label)

        self.indicator_widget.setLayout(self.indicator_layout)
        self._layout.addWidget(self.indicator_widget)

        self.connect = QPushButton

        self.setLayout(self._layout)
        self.setStyleSheet("border: 1px solid black;")



if __name__=="__main__":
    app = QApplication(sys.argv)
    mwindow = QWidget()
    status = BLEStatus("THINGY")
    mwindow.setGeometry(200, 200, 600, 600)
    mwindow.show()
    sys.exit(app.exec())