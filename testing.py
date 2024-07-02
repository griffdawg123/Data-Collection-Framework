import sys
from PyQt6.QtWidgets import QApplication, QComboBox, QLineEdit

if __name__ == "__main__":
    app = QApplication(sys.argv)
    line_edit = QLineEdit()
    combo = QComboBox()
    combo.setGeometry(0, 0, 240, 180)
    combo.setLineEdit(line_edit)
    combo.addItem("Hello")
    combo.show()
    sys.exit(app.exec())
