from bleak import BleakClient
from asyncio import BaseEventLoop

from src.ble.bit_parser import BitParser
class BLEConnection():
    def __init__(self, address: str, event_loop: BaseEventLoop) -> None:
        self.address = address
        self.client = BleakClient(address)
        self.event_loop = event_loop
        self.event_loop.create_task(self.connect())
        self.services = {}

    async def connect(self):
        # log attempted connect
        await self.client.connect()
        # log connect success/unsuccessful

    async def disconnect(self):
        # log attempted disconnect
        await self.client.disconnect()
        # log success/unsuccess

    def add_or_update_service(self, uuid: str, name: str, parser: BitParser):
        service = self.services.get(name, {})
        service["uuid"] = uuid
        service["parser"] = parser
        service["current_val"] = b'\x00' * parser.num_bytes
        self.services["name"] = service

    def remove_service(self, name: str):
        self.services.pop(name)

    def notify_callback(self):
        # self.
        return
    
if __name__=="__main__":
    pass
    


