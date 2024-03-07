import sys

import numpy as np
from PyQt5.QtWidgets import *

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from edf_to_csv import edf_to_csv

from plot_csv import plot


def convert():
    path = edf_file.get_file_path()
    edf_to_csv(path)

    if path.endswith('.edf'):
        csv_path = path.replace('.edf', '.csv')
        csv_file.file_path.setText(csv_path)


def load_csv():
    print("TEST")
    csv_data = pd.read_csv(csv_file.get_file_path())

    for i in reversed(range(plot_options_layout.count())): # prevent duplicates
        plot_options_layout.itemAt(i).widget().deleteLater()

    # need to clean header/column names (. in names causes problems, imagine will need more for other data)
    # e.g, clean_list = list of symbols to remove
    # for i in clean_list:
    # below line but '.' replaced with i so everything in list is removed from col names

    csv_data.columns = csv_data.columns.str.replace('.', '') # for cleaning

    col_list = list(csv_data.columns.values.tolist())
    col_list.pop(0) # remove time column

    # make plot options appear
    # make channel/plot options appear

    list_widget = QListWidget()

    list_widget.clear() # need to clear list, not working as intended at the moment

    list_widget.addItems(col_list)
    list_widget.setSelectionMode(QListWidget.MultiSelection) # allows selecting multiple channels

    # text entries for time
    start_time = QLineEdit()
    start_time.setPlaceholderText("Start")

    end_time = QLineEdit()
    end_time.setPlaceholderText("End")

    amount_time = QLineEdit()
    amount_time.setPlaceholderText("Amount of time")

    plot_button = QPushButton("Plot")
    plot_button.clicked.connect(lambda: plot_data(csv_data, list_widget, start_time, end_time))
    # i think lambda lets you pass arguments into function when pressing a button?

    # need to change something to prevent duplicates of widgets
    # maybe put in a separate options_layout, clear everytime "load" is pressed?
    plot_options_layout.addWidget(list_widget)

    plot_options_layout.addWidget(start_time)
    plot_options_layout.addWidget(end_time)
    plot_options_layout.addWidget(amount_time)

    plot_options_layout.addWidget(plot_button)

    options_layout.addLayout(plot_options_layout)


def plot_data(csv_data, list_widget, start_time, end_time):
    start = int(start_time.text())
    end = int(end_time.text())

    channels = []

    for item in list_widget.selectedItems():
        channels.append(item.text())    # get selected channel from list widget

    print(f"TEST - start {start}, end {end}, {channels}")

    fig, axs = plot(csv_data, channels, start, end)


    plt.show()

    #window_layout.addLayout(plot_layout) # works but need to extend window to see. must fix
    #plot_gui = PlotGui(csv_data, channels, start, end)
    #plot_gui.show()

    # want to try add to the gui instead of seperate window


class DatasetFilePicker(QWidget): # class used to prevent duplicate code
    def __init__(self, title, file_load, button_text):
        super().__init__()
        self.title = title # text at top of window when selecting file
        self.file_load = file_load # if loading edf or csv

        self.file_path = QLineEdit() # file path as text
        self.file_path.setReadOnly(True) # disable editing file path (may change later?)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

        self.load_button = QPushButton(button_text) # "convert" or "load"
        self.load_button.clicked.connect(self.file_load)

        options_layout = QVBoxLayout() # may change options_layout name
        options_layout.addWidget(self.file_path)
        options_layout.addWidget(self.browse_button)
        options_layout.addWidget(self.load_button)
        self.setLayout(options_layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.title, "", "All Files (*)")
        # may change "all files" for edf or csv only (if figure out how to do either), may need "file_type" variable
        if file_path:
            self.file_path.setText(file_path)

    def get_file_path(self):
        print(self)
        return self.file_path.text() # returns string of path for convertor/loader


class PlotGui(QWidget):
    def __init__(self, csv, channels, start, end):
        super().__init__()

        self.setLayout(plot_layout)
        canvas = self.create_plot(csv, channels, start, end)
        plot_layout.addWidget(canvas)


    def create_plot(self, csv, channels, start, end):
        fig, axs = plot(csv, channels, start, end)
        canvas = FigureCanvas(fig)
        return canvas


app = QApplication(sys.argv)
window = QWidget()
window_layout = QVBoxLayout()
options_layout = QVBoxLayout()
plot_options_layout = QVBoxLayout() # declared here to prevent duplicates
plot_layout = QVBoxLayout()
window.setLayout(window_layout)
window_layout.addLayout(options_layout)

edf_file = DatasetFilePicker("Select EDF file to convert to CSV", convert, "Convert")
options_layout.addWidget(edf_file)

csv_file = DatasetFilePicker("Select CSV file to load", load_csv, "Load")
options_layout.addWidget(csv_file)

# to do:
# prevent duplicates of list box, time entries and plot button if reloads/loads different csv
# try make plot appear in the gui?

window.show()

app.exec_()