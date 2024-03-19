import sys

import numpy as np
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from edf_to_csv import edf_to_csv

from plot_csv import plot


def convert():
    path = edf_file.get_file_path()
    edf_to_csv(path)

    if path.endswith('.edf'):
        csv_path = path.replace('.edf', '.csv')
        csv_file.file_path.setText(csv_path)


def select_all(col_list):
    for i in range(col_list.count()):
        col_list.item(i).setSelected(True)


def deselect_all(col_list):
    col_list.clearSelection()


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

    list_select_all = QPushButton('Select All')  # clears selection
    list_select_all.clicked.connect(lambda: select_all(list_widget))

    list_deselect_all = QPushButton('Deselect All') # clears selection
    list_deselect_all.clicked.connect(lambda: deselect_all(list_widget))

    # text entries for time
    int_validator = QIntValidator() # used to foce vals to be for int only

    start_time = QLineEdit()
    start_time.setValidator(int_validator)
    start_time.setPlaceholderText("Start")

    end_time = QLineEdit()
    end_time.setValidator(int_validator)
    end_time.setPlaceholderText("End")

    amount_time = QLineEdit()
    amount_time.setValidator(int_validator)
    amount_time.setPlaceholderText("Amount of time")


    plot_button = QPushButton("Plot")
    plot_button.clicked.connect(lambda: plot_data(csv_data, list_widget, start_time, end_time))
    # i think lambda lets you pass arguments into function when pressing a button?

    plot_options_layout.addWidget(list_widget)
    plot_options_layout.addWidget(list_select_all)
    plot_options_layout.addWidget(list_deselect_all)


    plot_options_layout.addWidget(start_time)
    plot_options_layout.addWidget(end_time)
    plot_options_layout.addWidget(amount_time)

    # onchange

    start_time.textChanged.connect(lambda: time_calculation(start_time, end_time, amount_time))
    end_time.textChanged.connect(lambda: time_calculation(start_time, end_time, amount_time))
    amount_time.textChanged.connect(lambda: time_calculation(start_time, end_time, amount_time))

    plot_options_layout.addWidget(plot_button)

    options_layout.addLayout(plot_options_layout)


def time_calculation(start, end, amount):
    try: # currently need way to clear all 3 values + let user still edit amount value
        if start.text() != "" and end.text() != "":
            new_amount = (int(start.text()) - int(end.text())) * -1
            amount.setText(str(new_amount))
        elif start.text() != "" and amount.text() != "":
            new_end = int(start.text()) + int(amount.text())
            end.setText(str(new_end))
        elif end.text() != "" and amount.text() != "":
            new_start = int(amount.text()) - int(end.text())
            start.setText(str(new_start))
    except ValueError:
        print("Invalid")
        pass

def plot_data(csv_data, list_widget, start_time, end_time):
    # for input validation, need to get file length to compare here
    if int(start_time.text()) < 0:
        print('Start time invalid')
    elif int(end_time.text()) < int(start_time.text()):
        print('End time invalid')
    else:
        start = int(start_time.text())
        end = int(end_time.text())

        channels = []

        for item in list_widget.selectedItems():
            channels.append(item.text())    # get selected channel from list widget

        print(f"TEST - start {start}, end {end}, {channels}")

        fig, axs = plot(csv_data, channels, start, end)




        #plt.show() #for outside of window plot

        window_layout.addLayout(plot_layout) # works but need to extend window to see. must fix (TEMP FIX)
        plot_gui = PlotGui(csv_data, channels, start, end)
        plot_gui.show()

        # text box (most likely not useful anyway, doesnt work for gui)
        #plt.text(((start - end) * - 1) / 2, 500, "test", size=50, rotation=30., ha="center", va="center", bbox=dict
        #(boxstyle="round", ec=(1., 0.5, 0.5), fc=(1., 0.8, 0.8), ))


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

        self.canvas = self.create_plot(csv, channels, start, end)

        toolbar = NavigationToolbar(self.canvas, self)
        plot_layout.addWidget(toolbar)

        plot_layout.addWidget(self.canvas)
        window.resize(450, 900) # TEMP FIX, plot atleast can be seen

    def create_plot(self, csv, channels, start, end):
        fig, axs = plot(csv, channels, start, end)
        canvas = FigureCanvas(figure=fig)
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
