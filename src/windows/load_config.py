from PyQt6.QtWidgets import QFileDialog

class LoadConfig(QFileDialog):
    def __init__(self):
        super().__init__()
        self.file_name = ""

    def get_file(self):
        self.file_name = QFileDialog.getOpenFileName(self,self.tr("Open Config"), "./config/workspaces/", self.tr("Config Files (*.config)"))
        return self.file_name

