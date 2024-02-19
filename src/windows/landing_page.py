from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout

class Landing(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.init_gui()

    def init_gui(self) -> None:
        self.setWindowTitle("Data Collection Framework")
        self.resize(720, 540)
        self.center()

        self.new_button = QPushButton(parent=self, text="New Workspace")
        self.new_button.setFixedSize(250, 75)

        self.load_button = QPushButton(parent=self, text="Load Workspace")
        self.load_button.setFixedSize(250, 75)

        self.layout = QVBoxLayout()
        self.layout.addStretch()
        self.layout.addWidget(self.new_button)
        self.layout.addWidget(self.load_button)
        self.layout.addStretch()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

    def center(self) -> None:
        screen_rect = self.frameGeometry()
        screen_geometry = self.screen().availableGeometry()
        centre_point = screen_geometry.center()
        screen_rect.moveCenter(centre_point)
        self.move(screen_rect.topLeft())