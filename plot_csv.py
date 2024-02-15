import sys

import numpy as np
import pandas as pd

import mne

import matplotlib
import matplotlib.pyplot as plt

import os.path
from pathlib import Path


from edf_to_csv import edf_to_csv

filename = 'chb01_02.edf'
# note, for some reason run window always shows
# "Extracting EDF parameters from C:\Users\R00212290\Desktop\Research Project\EEG-Viewer-Annotator\S001R01.edf..."
# ask why

# check if csv file exists

if filename.endswith('.edf'):
    filename = filename.replace('.edf', '')

csv_path = './' + filename + '.csv'
edf_path = './' + filename + '.edf'

check_csv_file = os.path.isfile(csv_path)
check_edf_file = os.path.isfile(edf_path)

if check_csv_file:
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

time_freq = 0
for index, row in csv_data.iterrows(): # use to double check
    if row['time'] != 1:
        time_freq += 1
    elif row['time'] == 1:
        #print(row['time'])
        break
#print(time_freq)

# user input from 1 to n where i = channel num (list all channels + corresponding num, ask for input, s)
col_list = list(csv_data.columns.values.tolist())

x = 0
for i in col_list:
    if x != 0:
        print(f"{x} - {i}")
    x += 1
col_num = 0
print(len(col_list))
while col_num < 1 or col_num >= len(col_list):
    col_num = int(input(f"Select channel to plot (between 1 and {len(col_list) - 1}) -> "))
    if col_num < 1 or col_num > len(col_list):
        print("Invalid input")
col_name = csv_data.columns[col_num]
col_name2 = csv_data.columns[col_num + 1] # for testing multiple plots

file_length = len(csv_data) / time_freq
print(f"EEG file is {file_length} seconds long")

time_amount = 0
min_time = -1
max_time = -1

mode = 0


def start_time(file_length, time_amount):
    min_time = -1
    while min_time < 0 or min_time > file_length - time_amount:
        min_time = int(input(f"Select start time to plot: "))
        if min_time < 0 or min_time > file_length:
            print("Invalid input")
    return min_time


def end_time(file_length, min_time):
    max_time = -1
    while max_time <= 0 or max_time > file_length:
        max_time = int(input(f"Select end time to plot: "))
        if max_time <= 0 or max_time > file_length or max_time < min_time:
            print("Invalid input")
    return max_time


# want to clean up to remove repeat functions
print("Select mode")
print("1 - Set amount of time")
print("2 - Set min and max time")
while mode == 0 or mode > 2:
    mode = int(input("-> "))

    if mode == 1:
        while time_amount <= 0 or time_amount > file_length:
            time_amount = int(input(f"Select amount of time to plot : "))
            if time_amount <= 0 or time_amount > file_length:
                print("Invalid input")
            elif time_amount == file_length:
                print("Plotting full data")
                min_time = 0
                max_time = file_length
            else:
                min_or_max = 0
                while min_or_max == 0 or min_or_max > 2:
                    print(f"Set 1: start time (min possible 0) or 2: end time (max possible {file_length})")
                    min_or_max = int(input("-> "))
                    if min_or_max == 0 or min_or_max > 2:
                        print("Invalid input")
                    elif min_or_max == 1:
                        min_time = start_time(file_length, time_amount)
                        max_time = min_time + time_amount
                    elif min_or_max == 2:
                        min_time = 0
                        max_time = end_time(file_length, min_time)
                        min_time = max_time - time_amount

    elif mode == 2:
        min_time = start_time(file_length, time_amount)
        max_time = end_time(file_length, min_time)

# want to let user chose num of subplots
# get data for each selected channel
# loop through array/list whatever for each plot
# will try thursday

fig, axs = plt.subplots(2)

plt.rcParams['lines.linewidth'] = 0.3

fig.suptitle(f"EEG Graph for {col_name} and {col_name2}")

axs[0].plot(csv_data.time, csv_data[col_name], 'tab:blue')
axs[1].plot(csv_data.time, csv_data[col_name2], 'tab:green')

for ax in axs.flat:
    ax.set(ylabel="Amplitude/Voltage (uV)")
    ax.set_xlim(min_time, max_time)

#axs[-1].set_xlim(xlabel="Time (S)")

plt.show()
