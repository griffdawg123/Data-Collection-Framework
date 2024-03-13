from bleak import BleakClient
from bleak.exc import BleakError
from src.ble.threads import DataThread
import asyncio
import numpy as np
from PyQt6.QtCore import pyqtSlot
from qasync import QEventLoop, QThreadExecutor, asyncClose

class BLEThread(DataThread):
    def __init__(self, device_address: str, service_uuid) -> None:
        super().__init__()
        self.uuid = service_uuid
        self.device_address = device_address
        self.client = BleakClient(self.device_address, lambda client: print(f"Disconnected from client: {client.address}"))
        self.loop = asyncio.get_event_loop()
        self.connect_task = self.loop.create_task(self.connect())
        self.current_val = b'\x00'

    async def connect(self):
        print(f"Connecting to {self.device_address}")
        await self.client.connect()
        print(f"Connected!")

    def cleanup(self):
        print("cleaning up")
        _ = self.disconnect()

    @asyncClose
    async def disconnect(self):
        print("disconnecting")
        await self.client.disconnect()
        print("disconnected successfully")

    def set_current_val(self, data: bytes):
        self.current_val = data

class ReadThread(BLEThread):
    def __init__(self, device_address: str, service_uuid) -> None:
        super().__init__(device_address, service_uuid)

    # updates current value and then emits it
    def get_value(self):
        try:
            if self.client.is_connected and self.client.services is not None:
                print("Device Connected")
                asyncio.run(self.read_value())
        except BleakError:
            print("Service Discovery Not Yet Completed")
        self.value.emit(float(np.frombuffer(self.current_val, dtype=np.int32)[0]))
    
    # reads current value from device
    async def read_value(self):
        self.current_val = await self.client.read_gatt_char(self.uuid)

class NotifyThread(BLEThread):
    def __init__(self, device_address: str, service_uuid) -> None:
        super().__init__(device_address, service_uuid)
        self.loop.create_task(self.init_notif())
        # asyncio.run(self.init_notif())

    def cleanup(self):
        self.loop.create_task(self.client.stop_notify(self.uuid))
        super().cleanup()

    def get_value(self):
        try:
            self.value.emit(float(np.frombuffer(self.current_val, dtype=np.int32)[0])/(2**16))
        except ValueError:
            self.value.emit(0)

    async def init_notif(self):
        await self.connect_task
        await self.client.start_notify(self.uuid, lambda char, data: self.set_current_val(data))
        

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
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    # 0409
    # EF68xxxx-9B35-4933-9B10-52FFA9740042
    # battery_graph = DataPlot(ReadThread("F1:EC:95:17:0A:62", "00002a19-0000-1000-8000-00805f9b34fb"), y_min=0, y_max=100, datarate=1)
    # battery_graph.show()
    # app.aboutToQuit.connect(battery_graph.cleanup)

    battery_graph = DataPlot(NotifyThread("F1:EC:95:17:0A:62", "EF680409-9B35-4933-9B10-52FFA9740042"), y_min=0, y_max=360, datarate=200, num_data_points=400)
    battery_graph.show()
    app.aboutToQuit.connect(battery_graph.cleanup)
    event_loop.run_forever()
        