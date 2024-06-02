from bleak import BleakClient


class GoodClient(BleakClient):
    def __init__(self, address):
        super.__init__(self, address)
        self.connected = False

    async def connect(self):
        self.connected = True

    async def disconnect(self):
        self.connected = False

    def is_connected(self):
        return self.connected
