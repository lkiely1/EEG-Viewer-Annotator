import gc
import json
import os
import sys
import matplotlib
import mne
import hashlib
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from edf_to_csv import edf_to_csv
from plot_eeg import plot

matplotlib.use('qt5agg')

dev_mode = 0  # 0 means load edf, 1 means load csv and convert edf to csv. keep on 0 as converting to csv isn't needed
bipolar_off = False  # set to true if you have issues with it on False. True will make it so program will not try to
# create bipolar channels from dataset (otherwise will try to create them if detects "-REF" in column names)


class FilePicker(QWidget):  # class used to prevent duplicate code
    def __init__(self, title, file_load, button_text):
        super().__init__()
        self.title = title  # text at top of window when selecting file
        self.file_load = file_load  # if loading edf or csv

        self.file_path = QLineEdit()  # file path as text
        self.file_path.setReadOnly(True)  # disable editing file path (may change later?)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

        self.load_button = QPushButton(button_text)  # "convert" or "load"
        self.load_button.clicked.connect(self.file_load)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.file_path)
        self.layout.addWidget(self.browse_button)
        self.layout.addWidget(self.load_button)
        self.setLayout(self.layout)
        main_layout.addLayout(self.layout)

    def browse_file(self):
        if self.file_load != change_directory:  # checking function being used, matching file type to what func used for
            if self.file_load == main_widget.load_dataset:
                file_filter = "EDF file (*.edf)"
            elif self.file_load == load_annots:
                file_filter = "TXT file (*.txt)"
            else:
                file_filter = "All Files (*)"
            file_path, _ = QFileDialog.getOpenFileName(self, self.title, "", file_filter)
        else:
            file_path = QFileDialog.getExistingDirectory(self, self.title, "")  # directory instead of file
        if file_path:
            self.file_path.setText(file_path)

    def get_file_path(self):
        return self.file_path.text()  # returns string of path


def convert():  # unused since not converting edf to csv anymore
    path = main_widget.edf_file.get_file_path()
    edf_to_csv(path)

    if path.endswith('.edf'):
        csv_path = path.replace('.edf', '.csv')
        main_widget.dataset_file.file_path.setText(csv_path)


def plot_data(data, list_widget, start_time, end_time):
    for i in reversed(range(plot_layout.count())):  # prevent duplicates, deletes prev widgets if exist
        plot_layout.itemAt(i).widget().deleteLater()

    if start_time.text() == "":
        print('Start time invalid')
        return
    elif end_time.text() == "":
        print('End time invalid')  # if user tries to plot without a time value
        return
    else:
        start = int(start_time.text())
        end = int(end_time.text())

        channels = []
        for item in list_widget.selectedItems():
            channels.append(item.text())  # get selected channel from list widget
        if len(channels) == 0:
            print('No channels selected')
            return

        for i in reversed(range(window_layout.count())):  # used to prevent visual issue with splitter if plotted before
            if window_layout.itemAt(i).widget() == plot_splitter:
                for i in reversed(range(plot_splitter.count())):
                    widget = plot_splitter.widget(i)
                    if widget is not None:
                        widget.setParent(None)
                        if widget is not main_widget:
                            widget.deleteLater()
                            gc.collect()  # don't think is doing anything, mem leak still exists

        plot_gui = PlotGuiWidget(data, channels, start, end)  # create plot widget

        plot_splitter.addWidget(main_widget)
        plot_splitter.addWidget(plot_gui)
        plot_splitter.setStretchFactor(0, 500)
        plot_splitter.setStretchFactor(1, 100)

        plot_splitter.setCollapsible(0, False)  # stops widgets from being able to be hidden
        plot_splitter.setCollapsible(1, False)

        window_layout.addWidget(plot_splitter)
        plot_gui.show()


class PlotGuiWidget(QWidget):
    def __init__(self, csv, channels, start, end):
        super().__init__()

        self.setLayout(plot_layout)

        self.canvas = self.create_plot(csv, channels, start, end)

        self.canvas.setMinimumWidth(600)  # prevents canvas being hidden when created

        toolbar = NavigationToolbar(self.canvas, self)  # toolbar for zoom/pan
        plot_layout.addWidget(toolbar)

        plot_layout.addWidget(self.canvas)

    def create_plot(self, dataframe, channels, start, end):
        annotations_file_path = main_widget.annot_win.annot_file.get_file_path()  # path for loaded annots if any
        global edfmd5
        global jsonpath
        user_annot_file = jsonpath + edfmd5 + "_annotations.txt"  # path for user created annots (defined multiple times, need to fix)
        fig, axs = plot(annotations_file_path, user_annot_file, dataframe, channels, start, end,
                        app)  # pass app to prevent crash
        canvas = FigureCanvas(figure=fig)
        return canvas


def getmd5(edf):
    # md5 is used for filename of user made annots file. seems to work very well. code here used to get hash of edf file
    md5 = hashlib.md5()
    f = open(edf, "rb")
    while chunk := f.read(4096):
        md5.update(chunk)

    return md5.hexdigest()  # md5 as string used for annotation txt file name


class MainGuiWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setLayout(main_layout)
        load_title = "Select EDF file to load"

        if dev_mode == 1:  # 1 means load csv, not used anymore
            self.edf_file = FilePicker("Select EDF file to convert to CSV", convert, "Convert")
            main_layout.addWidget(self.edf_file)
            load_title = "Select CSV file to load"

        self.dataset_file = FilePicker(load_title, self.load_dataset, "Load")
        main_layout.addWidget(self.dataset_file)

    def load_dataset(self):
        global edfmd5

        if dev_mode == 0:  # load edf
            if not os.path.isfile(main_widget.dataset_file.get_file_path()):
                return
            else:
                raw = mne.io.read_raw_edf(main_widget.dataset_file.get_file_path())
                data = raw.to_data_frame()
                bipolar = False
                for col in data.columns:
                    if bipolar_off == True:
                        bipolar = False
                        break
                    elif "-REF" in col or "-Ref" in col or "-ref" in col:  # checks for "-ref" in column name, if exists need to make bipolar
                        bipolar = True
                        break
                    else:
                        bipolar = False
                        # this way don't need user to select bipolar or not, and only works if data not bipolar yet

                if bipolar:
                    data.columns = data.columns.str.replace('EEG ', '')
                    data.columns = data.columns.str.replace('-REF', '')
                    data.columns = data.columns.str.replace('-Ref', '')
                    data.columns = data.columns.str.replace('-ref', '')  # for cleaning

                    new_data = pd.DataFrame()  # create new df temporarily

                    # only being tested on this dataset : https://zenodo.org/records/4940267
                    new_data.insert(0, 'time', data['time'])
                    new_data.insert(1, 'Fp1-F3', data['Fp1'] - data['F3'])
                    new_data.insert(2, 'F3-C3', data['F3'] - data['C3'])
                    new_data.insert(3, 'C3-P3', data['C3'] - data['P3'])
                    new_data.insert(4, 'P3-O1', data['P3'] - data['O1'])
                    new_data.insert(5, 'Fp2-F4', data['Fp2'] - data['F4'])
                    new_data.insert(6, 'F4-C4', data['F4'] - data['C4'])
                    new_data.insert(7, 'C4-P4', data['C4'] - data['P4'])
                    new_data.insert(8, 'P4-O2', data['P4'] - data['O2'])
                    new_data.insert(9, 'Fp1-F7', data['Fp1'] - data['F7'])
                    new_data.insert(10, 'F7-T3', data['F7'] - data['T3'])
                    new_data.insert(11, 'T3-T5', data['T3'] - data['T5'])
                    new_data.insert(12, 'T5-01', data['T5'] - data['O1'])
                    new_data.insert(13, 'Fp2-F8', data['Fp2'] - data['F8'])
                    new_data.insert(14, 'F8-T4', data['F8'] - data['T4'])
                    new_data.insert(15, 'T4-T6', data['T4'] - data['T6'])
                    new_data.insert(16, 'T6-O2', data['T6'] - data['O2'])
                    new_data.insert(17, 'Fz-Cz', data['Fz'] - data['Cz'])
                    new_data.insert(18, 'Cz-Pz', data['Cz'] - data['Pz'])

                    data = new_data  # put new df into old df
                time_freq = raw.info['sfreq']
        elif dev_mode == 1:  # load csv
            data = pd.read_csv(main_widget.dataset_file.get_file_path())
            time_freq = 0
            for index, row in data.iterrows():  # use to double-check
                if row['time'] != 1:
                    time_freq += 1
                elif row['time'] == 1:
                    break

        for i in reversed(range(plot_options_layout.count())):  # prevent duplicates
            widget = plot_options_layout.itemAt(i).widget()
            if widget is not None:  # crash if try to delete None widget so have to check it is not
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
                    break

        file_length = len(data) / time_freq  # len data = num of seconds * time frequency

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

        self.annot_win = AnnotationLoadWidget()

        annotation_load_button = QPushButton("Annotation load")
        annotation_load_button.clicked.connect(self.annotation_window_toggle)

        plot_options_layout.addWidget(list_widget, 0, 0, 1, 2)
        plot_options_layout.addWidget(list_select_all, 1, 0)
        plot_options_layout.addWidget(list_deselect_all, 1, 1)
        plot_options_layout.addWidget(annotation_load_button, 2, 0, 2, 2)

        label_w = data_time.sizeHint().width()  # set max width of below widgets to width of label
        data_time.setMaximumWidth(label_w)
        start_time.setMaximumWidth(label_w)
        end_time.setMaximumWidth(label_w)
        amount_time.setMaximumWidth(label_w)
        plot_button.setMaximumWidth(label_w)

        time_layout.addWidget(data_time)
        time_layout.addWidget(start_time)
        time_layout.addWidget(end_time)
        time_layout.addWidget(amount_time)
        time_layout.addWidget(plot_button)
        plot_options_layout.addLayout(time_layout, 0, 2)

        # onchange

        start_time.textChanged.connect(
            lambda: self.time_calculation(start_time, end_time, amount_time, int(file_length), 1))
        end_time.textChanged.connect(
            lambda: self.time_calculation(start_time, end_time, amount_time, int(file_length), 2))
        amount_time.textChanged.connect(
            lambda: self.time_calculation(start_time, end_time, amount_time, int(file_length), 3))

        main_layout.addLayout(plot_options_layout)

    def annotation_window_toggle(self, checked):
        # lets annotation window be toggleable, this way data loaded isn't deleted when closed
        if self.annot_win.isVisible():
            self.annot_win.hide()
        else:
            self.annot_win.show()

    def select_all(self, col_list):  # select everything in list widget
        for i in range(col_list.count()):
            col_list.item(i).setSelected(True)

    def deselect_all(self, col_list):  # deselect everything in list widget
        col_list.clearSelection()

    def time_calculation(self, start, end, amount, max_length, case):
        # used to automatically calculate 1 value if 2 are filled in (e.g., duration = diff between start and end)
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

            # if start.text() != "" and end.text() != "" and int(end.text()) < int(start.text()):
            #    end.setText(str(int(start.text()) + 1))
            # commented out as doesn't really work well in this way

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
            pass


class AnnotationLoadWidget(QWidget):  # for displaying annotations from loaded file or user generated ones
    def __init__(self):
        super().__init__()
        global edfmd5
        global jsonpath
        global user_annot_file

        annotations_layout = QVBoxLayout()
        self.label = QLabel("ANNOTATIONS MUST BE IN A TXT IN FORMAT (annotnum, start, end)")
        # color_label = QLabel("Types: 1 – Clean EEG, 2 – Device Interference, 3 – EMG, 4 – Movement, 5 – Electrode, 6 – HF ventilation, 7 – Biological Rhythm, 8 - Seizure")
        labels = ["Clean EEG", "Device Interference", "EMG", "Movement", "Electrode", "HF ventilation",
                  "Biological Rhythm", "Seizure", "?", "??", "???"]
        colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "magenta", "cyan", "black"]

        annotations_layout.addWidget(self.label)

        self.user_annots = QTableWidget()  # table widget used to display values
        self.user_annots.setColumnCount(3)
        self.user_annots.setRowCount(99)  # TEMP, need to get num of lines before adding anything

        self.loaded_annots = QTableWidget()
        self.loaded_annots.setColumnCount(3)
        self.loaded_annots.setRowCount(99)  # TEMP, need to get num of lines before adding anything

        edfmd5 = getmd5(main_widget.dataset_file.get_file_path())

        f = open('filepath.json')

        data = json.load(f)

        jsonpath = data['path']

        user_annot_file = jsonpath + edfmd5 + "_annotations.txt"

        self.user_label = QLabel("Annotations created in program")
        annotations_layout.addWidget(self.user_label)

        self.annot_folder = FilePicker("Select Directory", change_directory, "Set Directory")
        self.annot_folder.file_path.setText(jsonpath)
        annotations_layout.addWidget(self.annot_folder)

        if os.path.isfile(user_annot_file):
            with open(user_annot_file, 'r') as file:
                line_num = 1
                self.user_annots.setItem(0, 0, QTableWidgetItem("Annot Type"))
                self.user_annots.setItem(0, 1, QTableWidgetItem("Start Time"))
                self.user_annots.setItem(0, 2, QTableWidgetItem("End Time"))
                for line in file:
                    if line != "":
                        annotation = line.strip('\n').split(',')
                        # get annot label from annot num and display label instead
                        self.user_annots.setItem(line_num, 0, QTableWidgetItem(labels[int(annotation[0])]))
                        self.user_annots.setItem(line_num, 1, QTableWidgetItem(annotation[1]))
                        self.user_annots.setItem(line_num, 2, QTableWidgetItem(annotation[2]))
                        line_num += 1

        annotations_layout.addWidget(self.user_annots)

        self.annot_file = FilePicker("Select TXT file to load", load_annots, "Load")
        self.load_label = QLabel("Loaded annotations")
        annotations_layout.addWidget(self.load_label)
        annotations_layout.addWidget(self.annot_file)
        annotations_layout.addWidget(self.loaded_annots)
        self.setLayout(annotations_layout)


def load_annots():  # should be changed to avoid similar code to above and below
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


def change_directory():  # lets user change generated annot file dir + change table widget (not optimal)
    global jsonpath
    global edfmd5
    labels = ["Clean EEG", "Device Interference", "EMG", "Movement", "Electrode", "HF ventilation", "Biological Rhythm",
              "Seizure", "?", "??", "???"]
    if os.path.isfile("filepath.json"):
        with open('filepath.json', "w") as f:
            new_path = main_widget.annot_win.annot_folder.get_file_path()
            if new_path.endswith("/"):
                new_path = new_path[:-1]
            data = {"path": new_path + "/"}
            jsonpath = main_widget.annot_win.annot_folder.get_file_path() + "/"

            f.write(json.dumps(data, ensure_ascii=False))
    main_widget.annot_win.user_annots.clear()

    if os.path.isfile(new_path + "/" + edfmd5 + "_annotations.txt"):
        with open(new_path + "/" + edfmd5 + "_annotations.txt", 'r') as file:
            line_num = 1
            main_widget.annot_win.user_annots.setItem(0, 0, QTableWidgetItem("Annot Type"))
            main_widget.annot_win.user_annots.setItem(0, 1, QTableWidgetItem("Start Time"))
            main_widget.annot_win.user_annots.setItem(0, 2, QTableWidgetItem("End Time"))
            for line in file:
                if line != "":
                    annotation = line.strip('\n').split(',')
                    main_widget.annot_win.user_annots.setItem(line_num, 0, QTableWidgetItem(labels[int(annotation[0])]))
                    main_widget.annot_win.user_annots.setItem(line_num, 1, QTableWidgetItem(annotation[1]))
                    main_widget.annot_win.user_annots.setItem(line_num, 2, QTableWidgetItem(annotation[2]))
                    line_num += 1


edfmd5 = None  # def as none as global later
jsonpath = None
user_annot_file = None

if not os.path.isfile("filepath.json"):  # create json and/or dir if not exist
    print("CREATING JSON")
    if not os.path.isdir("annotations"):
        print("CREATING DIRECTORY")
        os.mkdir('annotations')
    with open('filepath.json', 'w') as file:
        path = {'path': "annotations/"}
        json.dump(path, file)

app = QApplication(sys.argv)
window = QWidget()
window_layout = QHBoxLayout()

plot_splitter = QSplitter(Qt.Horizontal)

main_layout = QVBoxLayout()  # layout all other layouts are added to
plot_options_layout = QGridLayout()  # declared here to prevent duplicates
time_layout = QVBoxLayout()
plot_layout = QVBoxLayout()
window.setLayout(window_layout)

main_widget = MainGuiWidget()
window_layout.addWidget(main_widget)

window.show()

app.exec_()
