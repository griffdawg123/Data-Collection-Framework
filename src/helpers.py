from PyQt6.QtWidgets import QWidget
from os import walk

def center(window: QWidget) -> None:
    """takes a QWidget and centres it in the screen

    Args:
        window (QWidget): The window to be centred
    """
    screen_rect = window.frameGeometry()
    screen_geometry = window.screen().availableGeometry()
    centre_point = screen_geometry.center()
    screen_rect.moveCenter(centre_point)
    window.move(screen_rect.topLeft())

def format_config_name(string: str) -> str:
    """Generates a config name by lower casing and joining a string with '_'

    Args:
        string (str): string to be converted to the config name

    Returns:
        str: the corresponding config name
    """
    return "_".join(string.lower().split())


def get_files(dir: str) -> list[str]:
    return next(walk(dir), (None, None, []))[2]