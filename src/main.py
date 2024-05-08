import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import pyqtSignal
from src.windows.workspace import Workspace
import logging
import time
from qasync import QEventLoop
import asyncio

DEBUG = True
LOGGING = True

log_name: str = "debug" if DEBUG else str(time.time())

if __name__=="__main__":
    app = QApplication(sys.argv)
    event_loop = QEventLoop(app)

    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    asyncio.set_event_loop(event_loop)
    workspace = Workspace(app)
    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())

    # pending = asyncio.all_tasks(event_loop)
    # loop = asyncio.new_event_loop()
    # loop.run_until_complete(asyncio.gather(*pending))
