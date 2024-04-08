from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QApplication

class NewDevice(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.name = QLineEdit(self)
        self.address = QLineEdit(self)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.init_ui()

    def init_ui(self):
        form = QFormLayout()
        form.addRow("Name: ", self.name)
        form.addRow("Address: ", self.address)
        form.addWidget(self.button_box)
        self.setLayout(form)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_text(self):
        return (self.name.text(), self.address.text())
    

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    dialog = NewDevice()
    if dialog.exec():
        print(dialog.get_text())
    exit(0)


