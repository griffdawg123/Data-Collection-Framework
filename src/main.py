import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from windows.landing_page import Landing

def main(argv: list[str]):
    app = QApplication(argv)
    window = Landing()
    window.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main(sys.argv)