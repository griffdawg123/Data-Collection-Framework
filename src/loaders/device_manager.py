from asyncio import Task, TaskGroup, get_event_loop
from typing import Any, Callable, Generator, List

from PyQt6.QtCore import QObject, pyqtSignal
from bleak import BleakClient

class Singleton(type):
    _instances = {}
    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwds)
        return cls._instances[cls]

class ConnectionMessenger(QObject):
    connected_signal = pyqtSignal(str, bool) # name of client, connection successful
    disconnected_signal = pyqtSignal(str) # name of client
    client_added = pyqtSignal(str) # name of client
    client_removed = pyqtSignal(str) # name of client
    notify_tasks_complete = pyqtSignal(bool)

class DeviceManager(metaclass=Singleton):

    def __init__(self, clients = {}) -> None:
        self.config = ""
        self.set_clients(clients)
        self.task_set = set()
        self.messenger = ConnectionMessenger()
        self.current_notify_tasks = []

    # Client Dict management

    def set_clients(self, clients):
        self.clients = clients
        for name in self.clients.keys():
            self.connect_client(name)

    def add_client(self, name: str, client: BleakClient):
        self.clients[name] = client
        self.connect_client(name)
        self.messenger.client_added.emit(name)

    def connect_to_add(self, func: Callable[[str], Any]):
        self.messenger.client_added.connect(func)

    def get_clients(self):
        return self.clients

    def remove_client(self, name: str):
        client = self.clients.get(name)
        self.disconnect_client(client)
        del self.clients[name]
        self.messenger.client_removed.emit(name)

    def connect_to_remove(self, func: Callable[[str], Any]):
        self.messenger.client_removed.connect(func)
    # Names
    def get_client_names(self):
        return list(self.clients.keys())

    # Connection Management

    def connect_client(self, name):
        loop = get_event_loop()
        client = self.clients[name]
        connection_task = loop.create_task(client.connect(), name=name)
        self.task_set.add(connection_task)
        connection_task.add_done_callback(self.task_set.discard)
        connection_task.add_done_callback(self.on_connect)


    def on_connect(self, task: Task[bool]):
        connection_okay = True
        try:
            task.result()
        except:
            connection_okay = False
        self.messenger.connected_signal.emit(task.get_name(), connection_okay)

    def connect_connected_callback(self, func: Callable[[str, bool], Any]):
        print("connecting callback")
        self.messenger.connected_signal.connect(func)

    def disconnect_client(self, client: BleakClient):
        loop = get_event_loop()
        disconnect_task = loop.create_task(client.disconnect(), name=client.address)
        self.task_set.add(disconnect_task)
        disconnect_task.add_done_callback(self.task_set.discard)
        disconnect_task.add_done_callback(self.on_disconnect)

    async def disconnect_all(self):
        for _, client in self.clients.items():
            await client.disconnect()

    def on_disconnect(self, task: Task[bool]):
        self.messenger.disconnected_signal.emit(task.get_name())

    # Notify tasks

    def start_notify(self, task_set: List):
        self.current_notify_tasks = task_set
        loop = get_event_loop()
        tg_task = loop.create_task(self.await_start_notify_tasks(task_set))
        tg_task.add_done_callback(lambda _: self.messenger.notify_tasks_complete.emit(True))

    async def await_start_notify_tasks(self, task_set: List):
        async with TaskGroup() as tg:
            for task in task_set:
                client: BleakClient = task["client"]
                UUID: str = task["UUID"]
                source: Generator = task["source"]
                tg.create_task(client.start_notify(UUID, lambda _, data: source.send(data)))

    def connect_notify_done(self, func: Callable[[bool], Any]):
        self.messenger.notify_tasks_complete.connect(func)

    def stop_notify(self):
        loop = get_event_loop()
        tg_task = loop.create_task(self.await_stop_notify_tasks())
        tg_task.add_done_callback(lambda _: self.messenger.notify_tasks_complete.emit(False))


    async def await_stop_notify_tasks(self):
        async with TaskGroup() as tg:
            for task in self.current_notify_tasks:
                client: BleakClient = task["client"]
                UUID: str = task["UUID"]
                tg.create_task(client.stop_notify(UUID))

    '''
    On Setup:
        - Load clients into device manager
        - Connect to them and emit signal
    On New Device Added:
        - Add Device to Dictionary
        - Connect to device and emit signal
    On Device Removed:
        - Remove Device from dictionary
        - Disconnect from device
    On Close:
        - Return Device List
    On Play:
        - Queue notify events
    On Stop:
        - Queue Stop notify
    '''

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from qasync import QEventLoop
    import asyncio

    app = QApplication(sys.argv)
    loop = QEventLoop(QApplication)
    asyncio.set_event_loop(loop)
    dm: DeviceManager = DeviceManager()
    dm.connect_connected_callback(print)
    dm.add_client("thingy", BleakClient("F1:EC:95:17:0A:62"))
    loop.run_forever()

