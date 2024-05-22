from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

from src.widgets.status_tray import StatusTray

class SetupColumn(QWidget):
    def __init__(self, status_tray: StatusTray, new_button, load_button, restart_button) -> None:
        super().__init__()
        self.label = QLabel("Setup Column")
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.c_layout = QVBoxLayout()
        self.c_layout.addWidget(self.label)
        self.c_layout.addWidget(status_tray)
        self.c_layout.addWidget(new_button)
        self.c_layout.addWidget(load_button)
        self.c_layout.addWidget(restart_button)
        self.setLayout(self.c_layout)
