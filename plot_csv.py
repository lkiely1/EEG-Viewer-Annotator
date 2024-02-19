import sys

import numpy as np
import pandas as pd

import mne

import matplotlib
import matplotlib.pyplot as plt

import os.path
from pathlib import Path

from edf_to_csv import edf_to_csv

filename = 'chb01_01.edf'
# note, for some reason run window always shows
# "Extracting EDF parameters from C:\Users\R00212290\Desktop\Research Project\EEG-Viewer-Annotator\S001R01.edf..."
# ask why

# check if csv file exists

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

csv_data = pd.read_csv(filename + '.csv')

# need to clean header/column names (. in names causes problems, imagine will need more for other data)
# e.g, clean_list = list of symbols to remove
# for i in clean_list:
# below line but '.' replaced with i so everything in list is removed from col names

csv_data.columns = csv_data.columns.str.replace('.', '')

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

# user input from 1 to n where i = channel num (list all channels + corresponding num, ask for input, s)
col_list = list(csv_data.columns.values.tolist())

x = 0
for i in col_list:
    if x != 0:
        print(f"{x} - {i}")
    x += 1

col_num = 0
col_names = []

x = True

while x:
    add = ''
    while col_num < 1 or col_num > len(col_list) - 1:
        try:
            col_num = int(input(f"Select channel to plot (between 1 and {len(col_list) - 1}) -> "))
        except:
            print('Please enter number for channel.')
            continue
        if col_num < 1 or col_num > len(col_list) - 1:
            print(f"Invalid input. {col_num} is not a valid channel number")
            continue
        elif csv_data.columns[col_num] in col_names:
            print("Channel already selected. Choose another")
            continue

        if col_num != 0:
            col_names.append(csv_data.columns[col_num])

    print(f"Currently plotting {col_names}")
    while add == '':
        add = str(input("Do you want to add another channel? (y/n) -> ")).lower().strip()
        if add != "y" and add != "n":
            print("Please say yes (y) or no (n)")
        elif add == 'y':
            col_num = 0
        elif add == 'n':
            x = False

file_length = len(csv_data) / time_freq
print(f"EEG file is {file_length} seconds long")

time_amount = 0
min_time = -1
max_time = -1

mode = 0


def start_time(file_length, time_amount):
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


def end_time(file_length, min_time):
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
    # axs.set(ylabel="Amplitude/Voltage (uV)")

else: # if only 1 in plot
    print("only 1 channel in plot")
    axs.plot(csv_data.time, csv_data[col_names[0]], 'tab:blue')
    axs.set(ylabel=f"{col_names[0]}")

    axs.set_xlim(min_time, max_time)  # need to get min max ylims

    axs.set(xlabel="Time (S)")
    axs.set(ylabel="Amplitude/Voltage (uV)")

plt.show()
