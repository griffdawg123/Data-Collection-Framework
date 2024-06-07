import sys
from typing import List
from PyQt6.QtWidgets import QApplication, QDialog, QFrame, QHBoxLayout, QLabel, QLayout, QPushButton, QTabWidget, QVBoxLayout, QWidget
from functools import partial

class GraphConfig(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.row_tabs = QTabWidget()
        self.graph_tabs = []
        self.init_UI()

    def init_UI(self):
        self.row_tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.row_tabs.addTab(QLabel("Press '+' to add a row"), "+")
        self.row_tabs.tabBarClicked.connect(self.handle_row_tabs_clicked)
        

        layout = QVBoxLayout()
        layout.addWidget(self.row_tabs)
        self.setLayout(layout)
        self.show()

    def handle_row_tabs_clicked(self, idx):
        if (self.row_tabs.count() - idx == 1):
            self.add_row()

    def add_row(self):
        new_tabs = QTabWidget()
        new_tabs.setTabPosition(QTabWidget.TabPosition.North)
        new_tabs.addTab(QLabel("Press '+' to add a graph"), "+")
        new_tabs.tabBarClicked.connect(partial(self.handle_graph_tabs_clicked, new_tabs))
        self.graph_tabs.append(new_tabs)
        self.row_tabs.insertTab(self.row_tabs.count()-1, new_tabs, str(self.row_tabs.count()))

    def handle_graph_tabs_clicked(self, row_tabs_widget, idx):
        print(row_tabs_widget.count(), idx)
        if (row_tabs_widget.count() - idx == 1):
            self.add_graph(row_tabs_widget)

    def add_graph(self, row_tabs_widget: QTabWidget):
        new_graph = QLabel("New Graph")
        row_tabs_widget.insertTab(row_tabs_widget.count() - 1, new_graph, str(row_tabs_widget.count()))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gc = GraphConfig()

    sys.exit(app.exec())
