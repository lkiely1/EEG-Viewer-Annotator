import sys
from memory_profiler import profile
import numpy as np
import pandas as pd

import mne
import gc

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('qt5agg')

import os.path
from pathlib import Path

from matplotlib.patches import Rectangle
from matplotlib.widgets import Slider

from edf_to_csv import edf_to_csv

@profile
def plot(annotations_file_path, md5, csv_data, col_names, min_time, max_time): # pass filepath into here
    fig, axs = plt.subplots(len(col_names)+1, sharey=True)

    plt.rcParams['lines.linewidth'] = 0.3

    fig.suptitle(f"EEG Graph for {col_names}")

    for i in range(len(col_names)):
        axs[i].plot(csv_data.time, csv_data[col_names[i]], 'tab:blue')
        axs[i].set(ylabel=f"{col_names[i]}")
        axs[i].set_xlim(min_time, max_time)  # need to get min max ylims

    axs[len(col_names)-1].set(xlabel="Time (S)")


    axs[len(col_names)].plot(csv_data.time, csv_data[col_names])
    axs[len(col_names)].set_xlim(0, csv_data.time.max())

    time_box = Rectangle((min_time, -300), abs(min_time - max_time), 500, edgecolor="grey",
                         fill=False, linewidth=5)
    axs[len(col_names)].add_patch(time_box)
    # 1 – Clean EEG, 2 – Device Interference, 3 – EMG, 4 – Movement, 5 – Electrode, 6 – HF ventilation, 7 – Biological Rhythm
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet", "magenta", "cyan", "black"]

    def annotate(annotate_type, annotation_num, annotation_x, annotation_x2, annotation_y, label):
        for i in range(len(col_names)+1):
            if annotation_num > 9:
                annotation_num = 9 # black if too high
            if annotate_type == "bg":
                # background colour
                axs[i].axvspan(annotation_x, annotation_x2, color=colors[annotation_num], alpha=0.3)
                label_pos = annotation_x + (abs(annotation_x2 - annotation_x)/2)
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
                label_pos = annotation_x + (abs(annotation_x2 - annotation_x) / 2)
                label_y_pos = -150

            if annotate_type != "arrow" and i != len(col_names):
                axs[i].annotate(label, (label_pos, label_y_pos))

    # axs.set(ylabel="Amplitude/Voltage (uV)") # not sure how to add back

    test_annot = 0

    if test_annot == 1:
        with open('annotation_test_file.txt', 'r') as file:
            for line in file:

                if line != "":
                    annotation = line.strip('\n').split(',')
                    # type, num, x, x2, y, label
                    annotate(annotation[0], int(annotation[1]), int(annotation[2]), int(annotation[3]),
                             int(annotation[4]), annotation[5])
    elif test_annot == 0: # want to change so user has to choose annotations NOT made w/ program!
        #file_name = os.path.basename(annotations_file_path)
        #expert = 'A' # possibly let user select expert (a, b or c)
        #txt_file = file_name.replace('.edf', '_' + expert + '.txt')
        #path = f"{os.path.dirname(annotations_file_path)}/annotations/{txt_file}" # change to just filepath from chosen annotations
        print(f" 1 {annotations_file_path}")
        if os.path.isfile(annotations_file_path):
            with open(annotations_file_path, 'r') as file:
                print("Test")
                for line in file:
                    if line != "":
                        annotation = line.strip('\n').split(',')
                        # type, num, x, x2, y, label
                        annotate("bar", int(annotation[0]), int(annotation[1]), int(annotation[2]),
                                                                                   0, "test from csv annots")
    if os.path.isfile(md5 + "_annotations.txt"):
        with open(md5 + "_annotations.txt", 'r') as file2:
            print("Test md5")
            for line in file2:
                if line != "":
                    annotation = line.strip('\n').split(',')
                    # type, num, x, x2, y, label
                    annotate("bar", int(annotation[0]), float(annotation[1]), float(annotation[2]),
                             0, "user created annot")
    else:
        print("TEST, No annotations")
    ##else: # if only 1 in plot
    #    print("only 1 channel in plot")
    #    axs.plot(csv_data.time, csv_data[col_names[0]], 'tab:blue')
    #    axs.set(ylabel=f"{col_names[0]}")

    #    axs.set_xlim(min_time, max_time)  # need to get min max ylims?

    #    axs.set(xlabel="Time (S)")
    #    axs.set(ylabel="Amplitude/Voltage (uV)")

    press = None
    annot_box = None
    init_x = None
    x2 = None
    annotation_num = None

    def on_click(event):
        global press
        global annot_box
        global init_x

        state = fig.canvas.toolbar.mode
        if event.inaxes == time_box.axes and state == "":
            press = True
            fig.canvas.mpl_connect('motion_notify_event', on_motion)
        elif event.inaxes != axs[-1] and state == "":
            press = True
            # create rectangle at x pos
            init_x = event.xdata
            annot_box = Rectangle((init_x, -200), width=0.1, height=75) # could change to bar values
            event.inaxes.add_patch(annot_box)
            fig.canvas.draw()
            fig.canvas.mpl_connect('motion_notify_event', on_motion)

    def on_motion(event):
        global press
        state = fig.canvas.toolbar.mode
        if press == True and event.inaxes == time_box.axes and state == "":
            x = event.xdata
            time_box.set_x(x)
            for i in range(len(col_names)):
                axs[i].set_xlim(x, x + (abs(min_time - max_time)))
            fig.canvas.draw()
            fig.canvas.mpl_connect('button_release_event', on_release)
        elif press == True and event.inaxes != axs[-1] and state == "":
            global annot_box
            global init_x
            global x2
            print("t")
            x2 = event.xdata
            width = x2 - annot_box.get_x()
            annot_box.set_width(width)
            fig.canvas.draw()
            fig.canvas.mpl_connect('button_release_event', on_release)
            # move rectangle
            # check incase user draws backwards (lowest x is start)

    def on_release(event):
        global press
        global annot_box
        global init_x
        global x2
        global annotation_num
        press = False
        if event.inaxes != axs[-1]:
            print("t")
            global init_x
            global x2
            global annotation_num
            if init_x > x2:
                start = x2
                end = init_x
                annot_len = abs(start - end)
            else:
                start = init_x
                end = x2
                annot_len = abs(start - end)
            for i in range(len(col_names)):
                axs[i].add_patch(Rectangle((start, -200), width=annot_len, height=75, facecolor='red', fill=True))
            fig.canvas.draw()
            # save to file
            filename = md5 # get md5 hash of eeg and use that for filenames?
            #if annotation_num is None:
            #    annotation_num = 0
            with open(filename + '_annotations.txt', 'a') as f:
                f.write(f'2,{start},{end}')
                f.write('\n')

            #annotation_num += 1

        # new window for data to edit
        fig.canvas.mpl_disconnect(on_click)
        fig.canvas.mpl_disconnect(on_motion)


    fig.canvas.mpl_connect('button_press_event', on_click)

    plt.tight_layout()

    return fig, axs

#TEST
#fig, axs = plot(pd.read_csv('chb01_02.csv'), ['FP1-F7', 'F7-T7'],1,120)
#plt.show()
