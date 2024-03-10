# https://anandology.com/blog/using-iterators-and-generators/
from abc import abstractmethod
from PyQt6.QtCore import QThread, pyqtSignal

class DataThread(QThread):

    value = pyqtSignal(float)

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_value(self, *args, **kwargs):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    
