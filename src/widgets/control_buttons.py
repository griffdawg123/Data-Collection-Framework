from PyQt6.QtWidgets import QApplication, QHBoxLayout, QPushButton, QWidget
import sys


class ControlButtons(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.play = QPushButton(">")
        self.pause = QPushButton("||")
        self.init_UI()

    def connect_funcs(self, play, pause):
        self.play.clicked.connect(play)
        self.pause.clicked.connect(pause)

    def init_UI(self):
        layout = QHBoxLayout()
        layout.addWidget(self.pause)
        layout.addWidget(self.play)
        self.setLayout(layout)

if __name__ == "__main__":

    def play():
        print("play")

    def pause():
        print("pause")


    app = QApplication(sys.argv)
    cb = ControlButtons()
    cb.connect_funcs(play, pause)
    cb.show()
    sys.exit(app.exec())
