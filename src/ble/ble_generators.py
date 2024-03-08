from bleak import BleakClient
from threads import DataThread
import asyncio
import numpy as np

class ReadThread(DataThread):
    def __init__(self, device_address: str, service_uuid) -> None:
        super().__init__()
        self.uuid = service_uuid
        self.device_address = device_address
        self.client = BleakClient(self.device_address)
        self.current_val = b'abc'

    # updates current value and then emits it
    def get_value(self):
        if self.client.is_connected:
            print("Device Connected")
            asyncio.run(self.read_value())
        self.value.emit(float(np.frombuffer(self.current_val, dtype=np.uint8)[0]))
    
    # reads current value from device
    async def read_value(self):
        self.current_val = await self.client.read_gatt_char(self.uuid)

if __name__ == "__main__":
    import os, sys
    from PyQt6.QtWidgets import QApplication
    myDir = os.getcwd()
    sys.path.append(myDir)
    from pathlib import Path
    path = Path(myDir)
    a=str(path.parent.absolute())
    sys.path.append(a)
    from src.widgets.data_plot import DataPlot

    app = QApplication(sys.argv)
    battery_graph: DataPlot = DataPlot(ReadThread("F1:EC:95:17:0A:62", "00002a19-0000-1000-8000-00805f9b34fb"), y_min=0, y_max=100, datarate=1)
    battery_graph.show()
    sys.exit(app.exec())
        