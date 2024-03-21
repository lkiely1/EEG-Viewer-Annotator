import sys

import numpy as np
import pandas as pd

import mne

import matplotlib
import matplotlib.pyplot as plt

import os.path
from pathlib import Path

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


def plot(csv_data, col_names, min_time, max_time):
    fig, axs = plt.subplots(len(col_names), sharex=True, sharey=True)

    plt.rcParams['lines.linewidth'] = 0.3

    fig.suptitle(f"EEG Graph for {col_names}")

    if len(col_names) > 1:
        for i in range(len(col_names)):
            axs[i].plot(csv_data.time, csv_data[col_names[i]], 'tab:blue')
            axs[i].set(ylabel=f"{col_names[i]}")

        for ax in axs.flat:
            ax.set_xlim(min_time, max_time)  # need to get min max ylims

        axs[-1].set(xlabel="Time (S)")

        def annotate(annotate_type, annotate_start_or_x_coord, annotate_end_or_y_coord, annotation_num, label):
            for i in range(len(col_names)):
                col = "red" # how do i assign colours to colour num??

                if annotate_type == "bg":
                    # background colour
                    axs[i].axvspan(annotate_start_or_x_coord, annotate_end_or_y_coord, color=col, alpha=0.3)

                elif annotate_type == "arrow":
                    axs[i].annotate(label, xy=(annotate_start_or_x_coord, annotate_end_or_y_coord), xytext=(3, 1.5),
                                    arrowprops=dict(facecolor=col, shrink=0.05), )

                elif annotate_type == "line":
                    axs[i].axvline(x=annotate_start_or_x_coord, color=col, linestyle='--')

        # axs.set(ylabel="Amplitude/Voltage (uV)")

        #call annotate function (testing)
        #annotate("bg", 50, 75, 0, "none")
        #annotate("arrow", 75, 100, 1, "Arrow")
        #annotate("line", 30, 0, 2, "none")

        with open('annotation_test_file.txt', 'r') as file:
            for line in file:
                print()
                if line != "":
                    annotation = line.strip('\n').split(',')
                    annotate(annotation[0], int(annotation[1]), int(annotation[2]), 0, annotation[3])

    else: # if only 1 in plot
        print("only 1 channel in plot")
        axs.plot(csv_data.time, csv_data[col_names[0]], 'tab:blue')
        axs.set(ylabel=f"{col_names[0]}")

        axs.set_xlim(min_time, max_time)  # need to get min max ylims

        axs.set(xlabel="Time (S)")
        axs.set(ylabel="Amplitude/Voltage (uV)")

    plt.tight_layout()

    return fig, axs

#TEST
#fig, axs = plot(pd.read_csv('chb01_02.csv'), ['FP1-F7', 'F7-T7'],1,120)
#plt.show()
