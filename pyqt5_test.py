import sys
from PyQt5.QtWidgets import *

from edf_to_csv import *

from plot_csv_tk import *


def convert():
    edf_to_csv(edf_file.get_file_path())
    # change csv file field to name of converted csv?


def load_csv():
    print("TEST")
    csv_data = pd.read_csv(csv_file.get_file_path())

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
    # maybe put in a separate layout, clear everytime "load" is pressed?
    layout.addWidget(list_widget)

    layout.addWidget(start_time)
    layout.addWidget(end_time)
    layout.addWidget(amount_time)

    layout.addWidget(plot_button)


def plot_data(csv_data, list_widget, start_time, end_time):
    start = int(start_time.text())
    end = int(end_time.text())

    channels = []

    for item in list_widget.selectedItems():
        channels.append(item.text())    # get selected channel from list widget

    print(f"TEST - start {start}, end {end}, {channels}")

    fig, axs = plot(csv_data, channels, start, end)
    plt.show()

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

        layout = QVBoxLayout() # may change layout name
        layout.addWidget(self.file_path)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.load_button)
        self.setLayout(layout)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.title, "", "All Files (*)")
        # may change "all files" for edf or csv only (if figure out how to do either), may need "file_type" variable
        if file_path:
            self.file_path.setText(file_path)

    def get_file_path(self):
        return self.file_path.text() # returns string of path for convertor/loader


app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout()
window.setLayout(layout)

edf_file = DatasetFilePicker("Select EDF file to convert to CSV", convert, "Convert")
layout.addWidget(edf_file)

csv_file = DatasetFilePicker("Select CSV file to load", load_csv, "Load")
layout.addWidget(csv_file)

# to do:
# prevent duplicates of list box, time entries and plot button if reloads/loads different csv
# try make plot appear in the gui?

window.show()

app.exec_()
