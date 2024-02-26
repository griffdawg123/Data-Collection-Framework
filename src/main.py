import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from windows.config_selection import ConfigSelection
import logging
import time

DEBUG = True
LOGGING = True

log_name = "debug" if DEBUG else str(time.time())

def set_config(config: str) -> None:
    print(config)

def main(argv: list[str]) -> None:
    logging.basicConfig(filename=f"./logs/{log_name}.log", encoding="utf-8", level=logging.DEBUG, format='%(asctime)s:%(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger("logger")    
    if not LOGGING: logging.disable()
    logger.info("Starting Application")
    app = QApplication(argv)
    config_selection = ConfigSelection(logger, set_config)
    config_selection.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main(sys.argv)