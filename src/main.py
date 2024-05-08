import sys
from PyQt6.QtWidgets import QApplication
from src.windows.workspace import Workspace
from qasync import QEventLoop
import asyncio

def main():
    # Create application and workspace window
    app = QApplication(sys.argv)
    workspace = Workspace(app) 

    # Extract event loop
    event_loop = QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    # Run app
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())


if __name__=="__main__":
    main()