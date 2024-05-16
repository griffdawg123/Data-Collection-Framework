from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
import string
from PyQt6.QtCore import Qt 

class Header(QWidget):
    def __init__(self, title) -> None: 
        super().__init__()
        self.header_layout = QVBoxLayout()
        self.title: QLabel = QLabel()
        self.title.setText(string.capwords(title))
        self.title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.title.setStyleSheet("border: 1px solid black; font-size: 40px;")
        self.header_layout.addWidget(self.title)

        self.control_buttons = QWidget()
        self.control_buttons.setFixedWidth(self.width()//2)
        self.save_button = QPushButton("Save Setup")
        self.play_button = QPushButton(">")
        self.pause_button = QPushButton("||")
        self.control_layout = QHBoxLayout()
        self.control_layout.addWidget(self.save_button)
        self.control_layout.addWidget(self.play_button)
        self.control_layout.addWidget(self.pause_button)
        self.control_buttons.setLayout(self.control_layout)
        self.header_layout.addWidget(self.control_buttons)

        self.setLayout(self.header_layout) 

    def setup_buttons(self, save, play, pause):
        self.save_button.clicked.connect(save)
        self.play_button.clicked.connect(play)
        self.pause_button.clicked.connect(pause)

