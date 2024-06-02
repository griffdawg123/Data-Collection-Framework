from PyQt6.QtWidgets import QFileDialog

class LoadDevice(QFileDialog):
    def __init__(self):
        super().__init__()
        self.file_name = ""

    def get_file(self):
        self.file_name = QFileDialog.getOpenFileName(self,self.tr("Open Config"), "./config/devices/", self.tr("Config Files (*.config)"))
        return self.file_name