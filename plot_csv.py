import sys

import numpy as np
import pandas as pd

import mne

import matplotlib
import matplotlib.pyplot as plt

import os.path
from pathlib import Path

from matplotlib.patches import Rectangle
from matplotlib.widgets import Slider

from edf_to_csv import edf_to_csv

#filename = 'chb01_01.edf'

# check if csv file exists
def file_check(filename):
    if filename.endswith('.edf'):
        filename = filename.replace('.edf', '')

    csv_path = './' + filename + '.csv'
    edf_path = './' + filename + '.edf'
    txt_path = './' + filename + '_info.txt'

    check_csv_file = os.path.isfile(csv_path)
    check_edf_file = os.path.isfile(edf_path)
    check_txt_file = os.path.isfile(txt_path)

    if check_csv_file and check_txt_file:
        print("CSV file already exists, opening")
    elif check_edf_file:
        print("CSV file doesn't exist for this EDF file, converting")
        edf_to_csv(filename)
    else:
        print("EDF file doesn't exist. Closing")
        sys.exit(0)





def time_freq_check(filename):
    if filename.endswith('.csv'):
        filename = filename.replace('.csv', '')
    csv_data = pd.read_csv(filename + '.csv')

    txt_path = './' + filename + '_info.txt'
    check_txt_file = os.path.isfile(txt_path)

    # get time
    # calculate time freq (e.g 256 lines in file2 and 3 is 1 sec)
    # read time col, count num of rows til reach 1
    time_freq_test = 0

    if check_txt_file:
        with open(filename + '_info.txt', 'r') as f:
            time_freq_test = float(f.readline())
        f.close()

    time_freq = 0
    for index, row in csv_data.iterrows():  # use to double check
        if row['time'] != 1:
            time_freq += 1
        elif row['time'] == 1:
            # print(row['time'])
            break
    # print(time_freq)

    if float(time_freq_test) == time_freq:
        print('same freq')
    else:
        print('error')


def channel_select(csv_data, col_num, col_names):
    col_names.append(csv_data.columns[col_num])
    return col_names # for selected channels, loop through listbox selections with this to add them all?
    # possibly use different approach?

"""
file_length = len(csv_data) / time_freq
print(f"EEG file is {file_length} seconds long")

time_amount = 0
min_time = -1
max_time = -1

mode = 0
"""


def start_time(file_length, time_amount): # user input in terminal not used anymore
    min_time = -1
    while min_time < 0 or min_time > file_length:
        try:
            min_time = int(input(f"Select start time to plot: "))
        except:
            print('Please enter a number for start time.')
            continue
        if min_time < 0 or min_time > file_length:
            print(f"Invalid input. Pick number between range {0} and {file_length}")
    return min_time


def end_time(file_length, min_time): # user input in terminal not used anymore
    max_time = -1
    while max_time <= 0 or max_time > file_length or max_time < min_time:
        try:
            max_time = int(input(f"Select end time to plot: "))
        except:
            print('Please enter a number for end time.')
            continue
        if max_time <= 0 or max_time > file_length or max_time < min_time:
            print(f"Invalid input. Pick number between range {min_time} and {file_length} ")
    return max_time


""" unused, was for when you would put plot details in run terminal
# want to clean up to remove repeat functions
print("Select mode")
print("1 - Set amount of time")
print("2 - Set min and max time")
while mode == 0 or mode > 2:
    try:
        mode = int(input("-> "))
    except:
        print('Please enter 1 or 2.')
        continue

    if mode == 1:
        while time_amount <= 0 or time_amount > file_length:
            try:
                time_amount = int(input(f"Select amount of time to plot : "))
            except:
                print('Please enter a number of time.')
                continue
            if time_amount <= 0 or time_amount > file_length:
                print(f"Invalid input. Pick number less than or equal to {file_length}")
            elif time_amount == file_length:
                print("Plotting full data")
                min_time = 0
                max_time = file_length
            else:
                min_or_max = 0
                while min_or_max == 0 or min_or_max > 2:
                    print(f"Set 1: start time (min possible 0) or 2: end time (max possible {file_length})")
                    try:
                        min_or_max = int(input("-> "))
                    except:
                        print('Invalid input. Please enter 1 or 2.')
                        continue
                    if min_or_max == 0 or min_or_max > 2:
                        print("Please enter 1 or 2")
                    elif min_or_max == 1:
                        min_time = start_time(file_length, time_amount)
                        max_time = min_time + time_amount
                    elif min_or_max == 2:
                        min_time = time_amount
                        max_time = end_time(file_length, min_time)
                        min_time = max_time - time_amount

    elif mode == 2:
        min_time = start_time(file_length, time_amount)
        max_time = end_time(file_length, min_time)
    else:
        print("Please enter 1 or 2")
"""


def plot(file_path, csv_data, col_names, min_time, max_time): # pass filepath into here
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
    elif test_annot == 0:
        file_name = os.path.basename(file_path)
        expert = 'A' # possibly let user select expert (a, b or c)
        txt_file = file_name.replace('.edf', '_' + expert + '.txt')
        print(file_name)
        print(txt_file)
        path = f"{os.path.dirname(file_path)}/annotations/{txt_file}"
        if os.path.isfile(path):
            with open(path, 'r') as file:
                print("Test")
                for line in file:
                    if line != "":
                        annotation = line.strip('\n').split(',')
                        # type, num, x, x2, y, label
                        annotate("bar", int(annotation[0]), int(annotation[1]), int(annotation[2]),
                                                                                   0, "test from csv annots")
    else:
        print("TEST, No annotations")
    ##else: # if only 1 in plot
    #    print("only 1 channel in plot")
    #    axs.plot(csv_data.time, csv_data[col_names[0]], 'tab:blue')
    #    axs.set(ylabel=f"{col_names[0]}")

    #    axs.set_xlim(min_time, max_time)  # need to get min max ylims?

    #    axs.set(xlabel="Time (S)")
    #    axs.set(ylabel="Amplitude/Voltage (uV)")

    #slider_ax = plt.axes([0.1, 0.05, 0.8, 0.03])
    #slider = Slider(slider_ax, "time", 0, (csv_data.time.max() - abs(min_time - max_time)), valinit=min_time)

    def on_click(event):
        x = event.xdata
        time_box.set_x(x)
        for i in range(len(col_names)):
            axs[i].set_xlim(x, x + (abs(min_time - max_time)))
        fig.canvas.draw()

    fig.canvas.mpl_connect('button_press_event', on_click)

    plt.tight_layout()

    return fig, axs

#TEST
#fig, axs = plot(pd.read_csv('chb01_02.csv'), ['FP1-F7', 'F7-T7'],1,120)
#plt.show()
