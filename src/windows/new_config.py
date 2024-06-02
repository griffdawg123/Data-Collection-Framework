from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel, QDialogButtonBox, QFileDialog, QInputDialog, QLineEdit, QBoxLayout
import src.helpers
from os import walk

CONFIG_PROMPT = "Please enter config name: "

class NewConfig(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.text = CONFIG_PROMPT
        self.initGUI()
        
    def initGUI(self) -> None:
        self.setWindowTitle("New Workspace")

        self.label = QLabel()
        self.label.setText(self.text)

        self.line_input = QLineEdit()
        self.line_input.textEdited.connect(self.set_label)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.toggle_ok(False)

        layout: QVBoxLayout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.line_input)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def set_label(self, text_input: str) -> None:
        self.text = text_input
        if self.text:
            self.label.setText(f"Config will be saved as: {src.helpers.format_config_name(self.text)}.config")
            if src.helpers.format_config_name(self.text) in [f.split(".")[0] for f in src.helpers.get_files("config/workspaces")]:
                self.label.setText(f"{src.helpers.format_config_name(self.text)}.config already exists.")
                self.toggle_ok(False)
            else:
                self.toggle_ok(True)
        else:
            self.label.setText(CONFIG_PROMPT)
            self.toggle_ok(False)

    def get_file_name(self) -> tuple[int, str]:
        return (self.exec(), self.text)
    
    def toggle_ok(self, enabled: bool) -> None:
        ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        if ok_button is not None:
            ok_button.setEnabled(enabled)




    

