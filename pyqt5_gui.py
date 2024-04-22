import gc
import os
import sys
from memory_profiler import profile
import matplotlib
import mne
import hashlib
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


matplotlib.use('qt5agg')

from edf_to_csv import edf_to_csv

from plot_csv import plot

dev_mode = 0    # 0 means load edf, 1 means load csv or convert


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

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.file_path)
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.load_button)
        self.setLayout(self.layout)
        main_layout.addLayout(self.layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.title, "", "All Files (*)")
        # may change "all files" for edf or csv only (if figure out how to do either), may need "file_type" variable
        if file_path:
            self.file_path.setText(file_path)

    def get_file_path(self):
        print(self)
        return self.file_path.text() # returns string of path for convertor/loader


def convert():
    path = main_widget.edf_file.get_file_path()
    edf_to_csv(path)

    if path.endswith('.edf'):
        csv_path = path.replace('.edf', '.csv')
        main_widget.dataset_file.file_path.setText(csv_path)


def plot_data(data, list_widget, start_time, end_time):
    # for input validation, need to get file length to compare here

    for i in reversed(range(plot_layout.count())): # prevent duplicates (though might be useful if want to compare data)
        plot_layout.itemAt(i).widget().deleteLater()

    if int(start_time.text()) < 0 or start_time.text() == "":
        print('Start time invalid')
    elif int(end_time.text()) < int(start_time.text()) or start_time.text() == "":
        print('End time invalid')
    else:
        start = int(start_time.text())
        end = int(end_time.text())

        channels = []

        for item in list_widget.selectedItems():
            channels.append(item.text())    # get selected channel from list widget

        print(f"TEST - start {start}, end {end}, {channels}")

        #file_path = main_widget.dataset_file.get_file_path()
        #fig, axs = plot(file_path, data, channels, start, end) made memory leak worse, wasnt even needed

        #plt.show() #for outside of window plot

        for i in reversed(range(window_layout.count())):  # kind of works?
            if window_layout.itemAt(i).widget() == plot_splitter:
                for i in reversed(range(plot_splitter.count())):
                    widget = plot_splitter.widget(i)
                    if widget is not None:
                        widget.setParent(None)
                        if widget is not main_widget:
                            widget.deleteLater()
                            gc.collect() # dont think is doing anything

        plot_gui = PlotGuiWidget(data, channels, start, end)


        #plot_splitter = QSplitter(Qt.Horizontal) # if remove atm cant plot twice, (canvas disappears), on 3rd crash

        plot_splitter.addWidget(main_widget)
        plot_splitter.addWidget(plot_gui)
        plot_splitter.setStretchFactor(0, 500) # not sure how exactly works rn
        plot_splitter.setStretchFactor(1, 100)

        plot_splitter.setCollapsible(0, False)
        plot_splitter.setCollapsible(1, False)

        window_layout.addWidget(plot_splitter)
        plot_gui.show()


class PlotGuiWidget(QWidget):
    @profile
    def __init__(self, csv, channels, start, end):
        super().__init__()

        self.setLayout(plot_layout)

        self.canvas = self.create_plot(csv, channels, start, end)

        self.canvas.setMinimumWidth(450)    # i think this is an ok fix? will ask if it shouldn't be hard coded like this

        toolbar = NavigationToolbar(self.canvas, self)
        plot_layout.addWidget(toolbar)

        plot_layout.addWidget(self.canvas)

    @profile
    def create_plot(self, dataframe, channels, start, end):
        annotations_file_path = main_widget.annot_win.annot_file.get_file_path()
        print(annotations_file_path)
        global edfmd5
        fig, axs = plot(annotations_file_path, edfmd5, dataframe, channels, start, end, app) # pass app to prevent crash
        canvas = FigureCanvas(figure=fig)
        return canvas


def getmd5(edf):
    md5 = hashlib.md5()
    f = open(edf, "rb")
    while chunk := f.read(4096):
        md5.update(chunk)

    return md5.hexdigest()


class MainGuiWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.annot_win = None
        self.setLayout(main_layout)
        load_title = "Select EDF file to load"

        if dev_mode == 1:
            self.edf_file = DatasetFilePicker("Select EDF file to convert to CSV", convert, "Convert")
            main_layout.addWidget(self.edf_file)
            load_title = "Select CSV file to load"

        self.dataset_file = DatasetFilePicker(load_title, self.load_dataset, "Load")
        main_layout.addWidget(self.dataset_file)

    def load_dataset(self):
        print("TEST")
        global edfmd5
        if dev_mode == 0:  # load edf
            raw = mne.io.read_raw_edf(main_widget.dataset_file.get_file_path())
            data = raw.to_data_frame()
            time_freq = raw.info['sfreq']
        elif dev_mode == 1:  # load csv
            data = pd.read_csv(main_widget.dataset_file.get_file_path())
            time_freq = 0
            for index, row in data.iterrows():  # use to double check
                if row['time'] != 1:
                    time_freq += 1
                elif row['time'] == 1:
                    # print(row['time'])
                    break

        print(f"time freq: {time_freq}")

        for i in reversed(range(plot_options_layout.count())):  # prevent duplicates
            widget = plot_options_layout.itemAt(i).widget()
            if widget is not None:  # crash if try to delete None widget?
                widget.setParent(None)
                widget.deleteLater()

        for i in reversed(range(time_layout.count())):  # prevent duplicates
            time_layout.itemAt(i).widget().deleteLater()

        # need to clean header/column names (. in names causes problems, imagine will need more for other data)
        # e.g, clean_list = list of symbols to remove
        # for i in clean_list:
        # below line but '.' replaced with i so everything in list is removed from col names

        data.columns = data.columns.str.replace('.', '')  # for cleaning

        col_list = list(data.columns.values.tolist())
        col_list.pop(0)  # remove time column

        # make plot options appear
        # make channel/plot options appear

        list_widget = QListWidget()

        list_widget.clear()  # not sure if still need this

        list_widget.addItems(col_list)
        list_widget.setSelectionMode(QListWidget.MultiSelection)  # allows selecting multiple channels

        list_select_all = QPushButton('Select All')  # clears selection
        list_select_all.clicked.connect(lambda: self.select_all(list_widget))

        list_deselect_all = QPushButton('Deselect All')  # clears selection
        list_deselect_all.clicked.connect(lambda: self.deselect_all(list_widget))

        if dev_mode == 1:
            time_freq = 0  # figure out better way to get time from edf
            for index, row in data.iterrows():
                if row['time'] != 1:
                    time_freq += 1
                elif row['time'] == 1:
                    # print(row['time'])
                    break

        file_length = len(data) / time_freq
        print(f"test, {file_length}")

        # label to let user know how long file is
        data_time = QLabel(f"Length of data: {int(file_length)}s")

        # text entries for time
        int_validator = QIntValidator(0, int(file_length))  # used to force vals to be for int only

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
        plot_button.clicked.connect(lambda: plot_data(data, list_widget, start_time, end_time))
        # i think lambda lets you pass arguments into function when pressing a button?

        self.annot_win = AnnotationLoadWidget()

        annotation_load_button = QPushButton("Annotation load")
        annotation_load_button.clicked.connect(self.annotation_window_toggle)

        plot_options_layout.addWidget(list_widget, 0, 0, 1, 2)
        plot_options_layout.addWidget(list_select_all, 1, 0)
        plot_options_layout.addWidget(list_deselect_all, 1, 1)
        plot_options_layout.addWidget(annotation_load_button, 2, 0, 2, 2)

        time_layout.addWidget(data_time)
        time_layout.addWidget(start_time)
        time_layout.addWidget(end_time)
        time_layout.addWidget(amount_time)
        time_layout.addWidget(plot_button)
        plot_options_layout.addLayout(time_layout, 0, 2)

        # onchange

        start_time.textChanged.connect(lambda: self.time_calculation(start_time, end_time, amount_time, int(file_length), 1))
        end_time.textChanged.connect(lambda: self.time_calculation(start_time, end_time, amount_time, int(file_length), 2))
        amount_time.textChanged.connect(lambda: self.time_calculation(start_time, end_time, amount_time, int(file_length), 3))

        main_layout.addLayout(plot_options_layout)

    def annotation_window_toggle(self, checked):
        if self.annot_win.isVisible():
            self.annot_win.hide()
        else:
            self.annot_win.show()

    def select_all(self, col_list):
        for i in range(col_list.count()):
            col_list.item(i).setSelected(True)

    def deselect_all(self, col_list):
        col_list.clearSelection()

    def time_calculation(self, start, end, amount, max_length, case):
        print(f"{str(start.text())}, {str(end.text())}, {str(amount.text())}, {max_length}, {case}")  # for testing
        try:  # currently if user tries to clear entry later, runs function twice to get val again. not sure how to stop
            # also must be why cant change amount value
            if start.text() != "" and end.text() != "" and (case == 1 or case == 2):
                new_amount = (int(start.text()) - int(end.text())) * -1
                amount.setText(str(new_amount))
            elif start.text() != "" and amount.text() != "" and (case == 1 or case == 3):
                new_end = int(start.text()) + int(amount.text())
                end.setText(str(new_end))
            elif end.text() != "" and amount.text() != "" and (case == 2 or case == 3):
                new_start = int(amount.text()) - int(end.text())
                start.setText(str(new_start))

            if int(start.text()) < 0:  # used to keep all 3 values in range 0 - file_length
                start.setText(str(0))

            if start.text() != "" and end.text() != "" and int(end.text()) < int(start.text()):
                end.setText(str(int(start.text()) + 1))

            if int(start.text()) >= max_length:
                start.setText(str(max_length - 1))

            if int(end.text()) > max_length:  # helpful when user just wants to do from start to end w/o typing max length
                if start.text() != "":
                    x = int(start.text())
                else:
                    x = 0
                end.setText(str(max_length - x))

            if int(amount.text()) > max_length:
                amount.setText(str(max_length))

        except ValueError:
            print("Invalid value")  # sometimes prints for what seems like no reason?
            pass


class AnnotationLoadWidget(QWidget):
    def __init__(self):
        super().__init__()
        global edfmd5
        annotations_layout = QVBoxLayout()
        self.label = QLabel("ANNOTATIONS MUST BE IN A TXT IN FORMAT (annotnum, start, end)")
        color_label = QLabel("Types: 1 – Clean EEG, 2 – Device Interference, 3 – EMG, 4 – Movement, 5 – Electrode, 6 – HF ventilation, 7 – Biological Rhythm, 8 - Seizure")
        labels = ["Clean EEG", "Device Interference", "EMG", "Movement", "Electrode", "HF ventilation", "Biological Rhythm", "Seizure", "?", "??", "???"]
        colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "magenta", "cyan", "black"]

        annotations_layout.addWidget(self.label)
        annotations_layout.addWidget(color_label)

        user_annots = QTableWidget()
        user_annots.setColumnCount(3)
        user_annots.setRowCount(99) # TEMP, need to get num of lines before adding anything

        self.loaded_annots = QTableWidget()
        self.loaded_annots.setColumnCount(3)
        self.loaded_annots.setRowCount(99)  # TEMP, need to get num of lines before adding anything

        edfmd5 = getmd5(main_widget.dataset_file.get_file_path()) # testing if parts work if this is here
        print(edfmd5)

        if os.path.isfile(edfmd5 + "_annotations.txt"):
            with open(edfmd5 + "_annotations.txt", 'r') as file:
                line_num = 1
                user_annots.setItem(0, 0, QTableWidgetItem("Annot Type"))
                user_annots.setItem(0, 1, QTableWidgetItem("Start Time"))
                user_annots.setItem(0, 2, QTableWidgetItem("End Time"))
                for line in file:
                    if line != "":
                        annotation = line.strip('\n').split(',')
                        user_annots.setItem(line_num, 0, QTableWidgetItem(labels[int(annotation[0])]))
                        user_annots.setItem(line_num, 1, QTableWidgetItem(annotation[1]))
                        user_annots.setItem(line_num, 2, QTableWidgetItem(annotation[2]))
                        line_num += 1

        self.user_label = QLabel("Annotations created in program")
        annotations_layout.addWidget(self.user_label)
        annotations_layout.addWidget(user_annots)

        self.annot_file = DatasetFilePicker("Select TXT file to load", load_annots, "Load")
        annotations_layout.addWidget(self.annot_file)
        annotations_layout.addWidget(self.loaded_annots)
        self.setLayout(annotations_layout)


def load_annots():
    labels = ["Clean EEG", "Device Interference", "EMG", "Movement", "Electrode", "HF ventilation", "Biological Rhythm",
              "Seizure", "?", "??", "???"]
    loaded_annots = main_widget.annot_win.loaded_annots
    if os.path.isfile(main_widget.annot_win.annot_file.get_file_path()):
        with open(main_widget.annot_win.annot_file.get_file_path(), 'r') as file:
            line_num = 1
            loaded_annots.setItem(0, 0, QTableWidgetItem("Annot Type"))
            loaded_annots.setItem(0, 1, QTableWidgetItem("Start Time"))
            loaded_annots.setItem(0, 2, QTableWidgetItem("End Time"))
            for line in file:
                if line != "":
                    annotation = line.strip('\n').split(',')
                    loaded_annots.setItem(line_num, 0, QTableWidgetItem(labels[int(annotation[0])]))
                    loaded_annots.setItem(line_num, 1, QTableWidgetItem(annotation[1]))
                    loaded_annots.setItem(line_num, 2, QTableWidgetItem(annotation[2]))
                    line_num += 1


class CreateAnnotation(QWidget):
    def __init__(self):
        super().__init__()
        annotation_layout = QVBoxLayout()
        color_label = QLabel("Types: 1 – Clean EEG, 2 – Device Interference, 3 – EMG, 4 – Movement, 5 – Electrode, 6 – HF ventilation, 7 – Biological Rhythm")
        annotation_layout.addWidget(color_label)

        start_time = QLineEdit()
        start_time.setPlaceholderText("Start")

        end_time = QLineEdit()
        end_time.setPlaceholderText("End")

        annotation_layout.addWidget(start_time)
        annotation_layout.addWidget(end_time)

        self.setLayout(annotation_layout)

edfmd5 = None

app = QApplication(sys.argv)
window = QWidget()
window_layout = QHBoxLayout()

plot_splitter = QSplitter(Qt.Horizontal)

main_layout = QVBoxLayout() # layout all other layouts are added to
plot_options_layout = QGridLayout() # declared here to prevent duplicates
time_layout = QVBoxLayout()
plot_layout = QVBoxLayout()
window.setLayout(window_layout)

main_widget = MainGuiWidget()
window_layout.addWidget(main_widget)

window.show()

app.exec_()
