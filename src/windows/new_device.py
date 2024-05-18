import asyncio
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QApplication, QComboBox 

from src import helpers
from src.ble import ble_scanner

LOADING_DEVICES = "--- Loading Devices ---"
MANUAL_ENTRY = "--- Enter Details ---"

class NewDevice(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.name = QLineEdit(self)
        self.address = QLineEdit(self)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Help | QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        if b := self.button_box.button(QDialogButtonBox.StandardButton.Help):
            b.setText("Reload")
        self.devices = [] 
        self.search_combobox = QComboBox() 
        self.search_combobox.addItem(LOADING_DEVICES)
        self.init_devices()
        self.init_combobox()
        self.init_ui()

    def init_ui(self):
        form = QFormLayout()
        form.addRow("Name: ", self.name)
        form.addRow("Address: ", self.address)
        form.addRow("Select Device: ", self.search_combobox)
        form.addWidget(self.button_box)
        self.setLayout(form)

        self.button_box.helpRequested.connect(self.init_devices)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def init_devices(self):
        self.search_combobox.clear()
        self.search_combobox.addItem(LOADING_DEVICES)
        self.event_loop = asyncio.get_event_loop()
        self.device_future = asyncio.Future(loop=self.event_loop)
        self.device_future.add_done_callback(self.set_devices)
        self.device_task = self.event_loop.create_task(ble_scanner.scan_for_devices(self.device_future))

    def init_combobox(self):
        def index_changed(idx):
            # print(f"Index changed to {idx}")
            if idx <= 0:
                self.set_entries("", "")
            else:
                d, _ = self.devices[idx-1]
                self.set_entries(helpers.format_config_name(d.name)+".config", d.address)
        self.search_combobox.currentIndexChanged.connect(lambda: index_changed(self.search_combobox.currentIndex()))

    def get_text(self):
        return (self.name.text(), self.address.text())
    
    def set_devices(self, future: asyncio.Future) -> None:
        self.devices = future.result()
        self.search_combobox.clear()
        self.search_combobox.addItem(MANUAL_ENTRY)
        self.search_combobox.addItems([f"{d.name}: {d.address}" for d, _ in self.devices])
        self.update()

    def set_entries(self, name, address):
        self.name.setText(name)
        self.address.setText(address)

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    dialog = NewDevice()
    if dialog.exec():
        print(dialog.get_text())
    exit(0)


