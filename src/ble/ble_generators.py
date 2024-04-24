from bleak import BleakClient
from bleak.exc import BleakError
from src.ble.threads import DataThread
from src.widgets.ble_datatype import BLEDataType
import asyncio
import numpy as np
from PyQt6.QtCore import pyqtSlot, pyqtSignal
from qasync import QEventLoop, QThreadExecutor, asyncClose

class BLEThread(DataThread):
    def __init__(self, client: BleakClient, UUID: str) -> None:
        super().__init__()
        self.uuid = UUID
        self.client = client
        self.loop = asyncio.get_event_loop()
        self.current_val = b'\x00'

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
    def __init__(self, client: BleakClient, service_uuid) -> None:
        super().__init__(client, service_uuid)

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

    def __init__(self, client: BleakClient, UUID: str) -> None:
        super().__init__(client, UUID)
        print("init")
        self.loop.create_task(self.init_notif())

    def cleanup(self):
        self.loop.create_task(self.client.stop_notify(self.uuid))
        super().cleanup()

    def get_value(self):
        print("Getting value")
        try:
            self.value.emit(float(np.frombuffer(self.current_val, dtype=np.int32)[0])/(2**16))
        except ValueError:
            self.value.emit(0)

    async def init_notif(self):
        self.status.emit("Starting notify")
        await self.client.start_notify(self.uuid, lambda char, data: self.set_current_val(data))
        self.status.emit("Notify Started")


if __name__ == "__main__":
    import time
    client = BleakClient("F1:EC:95:17:0A:62")
    UUID = "EF680409-9B35-4933-9B10-52FFA9740042"
    thread = NotifyThread(client, UUID)
    for i in range(50):
        print(thread.get_value())
        time.sleep(1)
    asyncio.run(thread.disconnect())
