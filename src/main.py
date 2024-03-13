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
    logging.basicConfig(filename=f"./logs/{log_name}.log", encoding="utf-8", level=logging.DEBUG, format='%(asctime)s:%(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger("logger")    
    if not LOGGING: logging.disable()
    logger.info("Starting Application")
    app = QApplication(sys.argv)
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    workspace = Workspace(logger, app)
    event_loop.run_forever()