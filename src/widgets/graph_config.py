import sys
from typing import Dict, List
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget, QDialogButtonBox
from functools import partial

from src.widgets.graph_form import ConfigForm

MAX_ROWS = 3
MAX_GRAPHS = 3

class GraphConfig(QDialog):
    def __init__(self, config = {}) -> None:
        super().__init__()
        self.data_rate = QSpinBox()
        self.data_rate.setRange(1, 100)
        self.data_rate.setValue(config.get("data_rate", 60))
        self.row_tabs: QTabWidget = QTabWidget()
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.remove_row_button = QPushButton("Remove Row")
        self.remove_row_button.setDefault(False)
        self.graph_tabs: List[QTabWidget] = []
        self.graphs = []
        self.at_max_rows = False
        self.init_UI()
        for row in config.get("rows", []):
            self.add_row(row)

    def init_UI(self):
        self.row_tabs.setTabPosition(QTabWidget.TabPosition.West)
        self.row_tabs.addTab(QLabel("Press '+' to add a row"), "+")
        self.row_tabs.tabBarClicked.connect(self.handle_row_tabs_clicked)
        self.remove_row_button.clicked.connect(self.remove_row)

        layout = QVBoxLayout()
        layout.addWidget(self.data_rate)
        layout.addWidget(self.row_tabs)
        layout.addWidget(self.remove_row_button)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_config(self):
        if not self.exec():
            return None
        config: Dict = {"data_rate" : self.data_rate.value()}
        rows = []
        print(self.graphs)
        for row in self.graphs:
            graphs = []
            for graph in row:
                print(graph)
                # if graph is not None:
                graphs.append(graph.get_config())
            rows.append(graphs)
        config["rows"] = rows
        return config

    # ---- Rows ---- 

    def handle_row_tabs_clicked(self, idx):
        if not self.at_max_rows:
            row_count = self.row_tabs.count()
            # if you clicked +
            if (row_count - idx == 1):
                self.add_row()
                # if we are now at the maximum rows
                if (row_count == MAX_ROWS):
                    self.row_tabs.setTabVisible(row_count, False)
                    self.at_max_rows = True

    def add_row(self, graphs = []):
        new_tabs: QTabWidget = QTabWidget()
        new_tabs.setTabPosition(QTabWidget.TabPosition.North)
        new_tabs.addTab(QLabel("Press '+' to add a graph"), "+")
        new_tabs.tabBarClicked.connect(partial(self.handle_graph_tabs_clicked, new_tabs, self.row_tabs.count()-1))
        self.graph_tabs.append(new_tabs)
        self.graphs.append([])
        self.row_tabs.insertTab(self.row_tabs.count()-1, new_tabs, str(self.row_tabs.count()))
        for graph in graphs:
            self.add_graph(new_tabs, len(self.graphs)-1, graph)


    def remove_row(self):
        # If we are at max --> Remove row and append + to the end
        # if we are not at max --> Remove row if current index is < count
        idx = self.row_tabs.currentIndex()
        if idx == self.row_tabs.count() - 1 and not self.at_max_rows:
            # do not delete +
            return
        self.row_tabs.removeTab(idx)
        self.graph_tabs.pop(idx)
        self.graphs.pop(idx)
        self.update_row_labels()
        if self.at_max_rows:
            self.row_tabs.setTabVisible(self.row_tabs.count()-1, True)
            self.at_max_rows = False

        if self.row_tabs.count() > 1 and self.row_tabs.currentIndex() == self.row_tabs.count() - 1:
            # If we have more than one tab and we are put on the last one (+)
            self.row_tabs.setCurrentIndex(self.row_tabs.count()-2)


    def update_row_labels(self):
        for i in range(len(self.graph_tabs)):
            self.row_tabs.setTabText(i, str(i+1))

    # ---- Graphs ---- 

    def handle_graph_tabs_clicked(self, row_tabs_widget: QTabWidget, row_idx, idx):
        if row_tabs_widget.count() <= MAX_GRAPHS:
            graph_count = row_tabs_widget.count()
            if (graph_count - idx == 1):
                self.add_graph(row_tabs_widget, row_idx)
                if (graph_count == MAX_GRAPHS):
                    row_tabs_widget.setTabVisible(graph_count, False)

    def add_graph(self, row_tabs_widget: QTabWidget, row_idx, graph_config = {}):
        new_graph = QWidget()
        new_graph_layout = QVBoxLayout()
        new_graph_form = ConfigForm(graph_config)
        new_graph_button = QPushButton("Remove Graph")
        new_graph_layout.addWidget(new_graph_form)
        new_graph_layout.addWidget(new_graph_button)
        new_graph.setLayout(new_graph_layout)
        new_graph_button.clicked.connect(partial(self.remove_graph, row_tabs_widget, row_idx))
        row_tabs_widget.insertTab(row_tabs_widget.count() - 1, new_graph, str(row_tabs_widget.count()))
        self.graphs[row_idx].append(new_graph_form)

    def remove_graph(self, row_tabs_widget: QTabWidget, row_idx):
        # If we are at max --> Remove row and append + to the end
        # if we are not at max --> Remove row if current index is < count
        idx = row_tabs_widget.currentIndex()
        graph_count = row_tabs_widget.count()
        if idx == graph_count - 1 and graph_count <= MAX_GRAPHS:
            # do not delete +
            return

        if graph_count > MAX_GRAPHS: # graphs are MAX_GRAPHS + "+"
            # turn + visible again
            row_tabs_widget.setTabVisible(graph_count-1, True)

        row_tabs_widget.removeTab(idx)
        self.graphs[row_idx].pop(idx)
        self.update_graph_labels(row_tabs_widget)

        if graph_count > 1 and idx == graph_count - 2:
          # If we have more than one tab and we are put on the last one (+)
            row_tabs_widget.setCurrentIndex(graph_count-3)


    def update_graph_labels(self, row_tabs_widget: QTabWidget):
        for i in range(row_tabs_widget.count()-1):
            row_tabs_widget.setTabText(i, str(i+1))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gc = GraphConfig()
    print(gc.get_config())
    sys.exit()
    # sys.exit(app.exec())
