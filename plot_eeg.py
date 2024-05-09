from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import *

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('qt5agg')

import os.path
from pathlib import Path

from matplotlib.patches import Rectangle

save = None
new_start = None
new_end = None


class CreateAnnotation(QWidget): # new window for when user is about to create new annot
    def __init__(self, start, end, fig, axs, col_names, user_annot_file, annot_len, annot_box):
        super().__init__()
        annotation_layout = QVBoxLayout()
        labels = ["Clean EEG", "Device Interference", "EMG", "Movement", "Electrode", "HF ventilation",
                  "Biological Rhythm", "Seizure", "?", "??", "???"]
        colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "magenta", "cyan", "black"]

        label = QLabel("Annotation Type")
        annotation_layout.addWidget(label)
        list_widget = QListWidget()

        list_widget.clear()

        list_widget.addItems(labels) # list box for all annot types
        list_widget.setCurrentRow(0) # default of clean eeg
        annotation_layout.addWidget(list_widget)

        start_validator = QIntValidator(0, end)
        end_validator = QIntValidator(start, 10000000)  # get max len
        # change when start/end changed?

        start_time = QLineEdit()
        start_time.setValidator(start_validator)
        start_time.setPlaceholderText("Start")

        end_time = QLineEdit()
        end_time.setValidator(end_validator)
        end_time.setPlaceholderText("End")


        start_time.setText(str(start)) # start/end = values from selected range w/time box
        end_time.setText(str(end))

        # run when changed
        start_time.textChanged.connect(lambda: self.update_box(start_time, end_time, fig, axs, annot_box))
        end_time.textChanged.connect(lambda: self.update_box(start_time, end_time, fig, axs, annot_box))

        annotation_layout.addWidget(start_time)
        annotation_layout.addWidget(end_time)

        # run if saving/cancelling
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_annot(start_time, end_time, fig, axs, col_names, user_annot_file, annot_len, list_widget.currentRow(), annot_box))

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.cancel(fig, axs, annot_box))

        annotation_layout.addWidget(save_button)
        annotation_layout.addWidget(cancel_button)

        self.setLayout(annotation_layout)

    def save_annot(self, start, end, fig, axs, col_names, user_annot_file, annot_len, annot_num, annot_box):
        new_start = int(start.text())
        new_end = int(end.text())
        new_annot_len = abs(new_end - new_start)

        labels = ["Clean EEG", "Device Interference", "EMG", "Movement", "Electrode", "HF ventilation",
                  "Biological Rhythm", "Seizure", "?", "??", "???"]
        colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "magenta", "cyan", "black"]

        print("Saving annotation...")
        for i in range(len(col_names)+1):
            axs[i].add_patch(Rectangle((new_start, -200), width=new_annot_len, height=75, facecolor=colors[annot_num], fill=True))
            if i != len(col_names) + 1:
                label_pos = new_start
                label_y_pos = -200  # drawn on bar
                axs[i].annotate(labels[annot_num], (label_pos, label_y_pos)) # add new annot to screen
        fig.canvas.draw()
        # save to file
        with open(user_annot_file, 'a') as f: # save new annot to file
            f.write(f'{annot_num},{new_start},{new_end}')
            f.write('\n')

        annot_box.remove() # remove box
        fig.canvas.draw()

        self.close()

    def cancel(self, fig, axs, annot_box):
        annot_box.remove() # remove box
        fig.canvas.draw()
        self.close()

    def update_box(self, start_time, end_time, fig, axs, annot_box): # change annot box if values for new annot changed
        # unsure if this should be used or not...
        #if int(start_time.text()) > int(end_time.text()):
        #    start = start_time.text()
        #    end = end_time.text()

        #    start_time.setText(end)
        #    end_time.setText(start)

        # works, can improve abit maybe
        width = abs(int(start_time.text()) - int(end_time.text())) # get new width
        annot_box.set_x(int(start_time.text())) # set new x start point
        annot_box.set_width(width) # set new width
        fig.canvas.draw()


def save_annotation(start, end, app, fig, axs, col_names, user_annot_file, annot_len, annot_box):
    start = round(start) # prevent very long floats
    end = round(end)
    window = CreateAnnotation(start, end, fig, axs, col_names, user_annot_file, annot_len, annot_box)
    # new window to let user update new annot if needed
    window.show()


#@profile
def plot(annotations_file_path, user_annot_file, eeg_data, col_names, min_time, max_time, app):  # pass filepath into here
    fig, axs = plt.subplots(len(col_names) + 1, sharey=True)

    plt.rcParams['lines.linewidth'] = 0.3

    fig.suptitle(f"EEG Graph for {col_names}")

    for i in range(len(col_names)):
        axs[i].plot(eeg_data.time, eeg_data[col_names[i]], 'tab:blue')
        axs[i].set(ylabel=f"{col_names[i]}")
        axs[i].set_xlim(min_time, max_time)  # need to get min max ylims

    axs[len(col_names) - 1].set(xlabel="Time (S)")

    axs[len(col_names)].plot(eeg_data.time, eeg_data[col_names]) # plot time againsts data in channels
    axs[len(col_names)].set_xlim(0, eeg_data.time.max()) # xlim = 0 til end of time in df

    time_box = Rectangle((min_time, -300), abs(min_time - max_time), 500, edgecolor="grey",
                         fill=False, linewidth=5) # box for time shown
    axs[len(col_names)].add_patch(time_box)

    labels = ["Clean EEG", "Device Interference", "EMG", "Movement", "Electrode", "HF ventilation", "Biological Rhythm", "Seizure", "?", "??", "???"]
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "magenta", "cyan", "black"]

    def annotate(annotate_type, annotation_num, annotation_x, annotation_x2, annotation_y, label):
        for i in range(len(col_names) + 1): # func to draw annotations
            if annotation_num > 9:
                annotation_num = 9  # black if too high
            if annotate_type == "bg":
                # background colour
                axs[i].axvspan(annotation_x, annotation_x2, color=colors[annotation_num], alpha=0.3)
                label_pos = annotation_x + (abs(annotation_x2 - annotation_x) / 2)
                label_y_pos = 100

            elif annotate_type == "arrow":
                axs[i].annotate(label, xy=(annotation_x, annotation_y),
                                xytext=(annotation_x - 10, annotation_y + 10),
                                arrowprops=dict(facecolor=colors[annotation_num], shrink=0.05))

            elif annotate_type == "line":
                axs[i].axvline(x=annotation_x, color=colors[annotation_num], linestyle='--')
                label_pos = annotation_x + 1
                label_y_pos = 100

            elif annotate_type == "box":
                axs[i].add_patch(Rectangle((annotation_x, annotation_y), annotation_x2 - annotation_x, 500,
                                           edgecolor=colors[annotation_num], fill=False, linewidth=5))
                label_pos = annotation_x + (abs(annotation_x2 - annotation_x) / 2)
                label_y_pos = annotation_y + 50

            elif annotate_type == "bar":
                axs[i].add_patch(Rectangle((annotation_x, -200), annotation_x2 - annotation_x, 75,
                                           facecolor=colors[annotation_num], fill=True))
                label_pos = annotation_x
                label_y_pos = -200 # drawn on bar

            if annotate_type != "arrow" and i != len(col_names):
                axs[i].annotate(label, (label_pos, label_y_pos))

    # axs.set(ylabel="Amplitude/Voltage (uV)") # not sure how to add back

    test_annot = 0 # unused, should always be 0

    if test_annot == 1:
        with open('annotation_test_file.txt', 'r') as file:
            for line in file: # used to just test annotations w/o specifying eeg data

                if line != "":
                    annotation = line.strip('\n').split(',')
                    # type, num, x, x2, y, label
                    annotate(annotation[0], int(annotation[1]), int(annotation[2]), int(annotation[3]),
                             int(annotation[4]), annotation[5])
    elif test_annot == 0:  # want to change so user has to choose annotations NOT made w/ program!
        if os.path.isfile(annotations_file_path):
            with open(annotations_file_path, 'r') as file:
                for line in file:
                    if line != "":
                        annotation = line.strip('\n').split(',')
                        # type, num, x, x2, y, label
                        annotate("bar", int(annotation[0]), int(annotation[1]), int(annotation[2]),
                                 0, labels[int(annotation[0])])
    if os.path.isfile(user_annot_file):
        with open(user_annot_file, 'r') as file2:
            for line in file2:
                if line != "":
                    annotation = line.strip('\n').split(',')
                    # type, num, x, x2, y, label
                    annotate("bar", int(annotation[0]), int(annotation[1]), int(annotation[2]),
                             0, labels[int(annotation[0])])
    else:
        print("Not loading annotations from other file")

    press = None
    annot_box = None
    init_x = None
    x2 = None
    annotation_num = None

    def on_click(event): # run when user clicks on plot
        global press
        global annot_box
        global init_x

        state = fig.canvas.toolbar.mode # to let user still use toolbar
        if event.inaxes == time_box.axes and state == "":
            press = True
            fig.canvas.mpl_connect('motion_notify_event', on_motion) # for moving time along
        elif event.inaxes != axs[-1] and state == "": # for creating annot
            press = True
            # create rectangle at x pos
            init_x = event.xdata
            annot_box = Rectangle((init_x, -200), width=0.1, height=500, fill=False)  # could change to bar values
            event.inaxes.add_patch(annot_box)
            fig.canvas.draw()
            fig.canvas.mpl_connect('motion_notify_event', on_motion)

    def on_motion(event):
        global press
        state = fig.canvas.toolbar.mode
        if press == True and event.inaxes == time_box.axes and state == "":
            x = event.xdata
            time_box.set_x(x) # move time box
            for i in range(len(col_names)):
                axs[i].set_xlim(x, x + (abs(min_time - max_time))) # move shown time
            fig.canvas.draw()
            fig.canvas.mpl_connect('button_release_event', on_release)
        elif press == True and event.inaxes != axs[-1] and state == "":
            global annot_box
            global init_x
            global x2
            x2 = event.xdata
            width = x2 - annot_box.get_x()
            annot_box.set_width(width) # extend drawn annot
            fig.canvas.draw()
            fig.canvas.mpl_connect('button_release_event', on_release)
            # move rectangle

    def on_release(event):
        global press
        global annot_box
        global init_x
        global x2
        global annotation_num
        press = False
        if event.inaxes != axs[-1]: # start creating annot
            global init_x
            global x2
            global annotation_num
            if init_x > x2: # swap start and end times if needed
                start = x2
                end = init_x
                annot_len = abs(start - end)
            else:
                start = init_x
                end = x2
                annot_len = abs(start - end)

            save_annotation(start, end, app, fig, axs, col_names, user_annot_file, annot_len, annot_box)

        fig.canvas.mpl_disconnect(on_click)
        fig.canvas.mpl_disconnect(on_motion)

    fig.canvas.mpl_connect('button_press_event', on_click)

    plt.tight_layout()

    return fig, axs

