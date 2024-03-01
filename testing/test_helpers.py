import src.helpers
from PyQt6.QtWidgets import QWidget

# tests that center function correctly positions a window
def test_center(qtbot):
    widget = QWidget()
    qtbot.addWidget(widget)

    # gets the height and width of the screen the widget resides in
    screen_height = widget.screen().availableGeometry().height()
    screen_width = widget.screen().availableGeometry().width()

    # gets the height and width of the widget
    widget_height = widget.frameGeometry().height()
    widget_width = widget.frameGeometry().width()

    # centred x and y pos is the top left corner of the window
    centred_y_pos = (screen_height / 2) - (widget_height / 2)
    centred_x_pos = (screen_width / 2) - (widget_width / 2)

    src.helpers.center(widget)

    assert widget.pos().x() == centred_x_pos
    assert widget.pos().y() == centred_y_pos

def test_format_config_name():
    assert src.helpers.format_config_name("hello") == "hello" # no changes
    assert src.helpers.format_config_name("hello world") == "hello_world" # sub space for underscore
    assert src.helpers.format_config_name("Hello") == "hello" # lower case
    assert src.helpers.format_config_name("Hello World") == "hello_world" # lower case and underscore

def test_get_files(tmp_path):

    FILE_NAME = "hello_world.txt"

    d = tmp_path / "sub"
    d.mkdir()
    p = d / FILE_NAME
    p.write_text("Hello World!")

    assert len(src.helpers.get_files(tmp_path / "sub")) == 1
    assert src.helpers.get_files(tmp_path / "sub")[0] == FILE_NAME
