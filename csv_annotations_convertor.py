import os
import sys

import mne
import numpy as np

import pandas as pd

### used for csv annotations from this dataset:
def annotations_convertor(filepath):
    print("test")
    # open csv file
    df = pd.read_csv(filepath)

    filename = os.path.basename(filepath)
    print(filename)
    # split filename by _ if any

    filename_details = filename.strip('.csv').split('_')
    print(filename_details)

    for column in df.columns:
        with open(f"{os.path.dirname(filepath)}/annotations/eeg{column}_{filename_details[2]}.txt", 'w') as file:
            print(f"column: {column}")
            annotation_num = 1
            last_1 = False
            duration = 0
            for index, row in df.iterrows():
                current = row[column]
                # check if current == NaN, skip col and save time if yes
                if current == 1.0 and last_1 != True:
                    start = int(index)
                    last_1 = True
                elif current == 1.0 and last_1 == True:
                    duration += 1
                elif current == 0 and last_1 == True:
                    last_1 = False
                    end = start + duration
                    file.write(f'{annotation_num},{start},{end}')
                    file.write('\n')
                    annotation_num += 1
                    start = 0
                    duration = 0
        #next col


annotations_convertor('C:/Users/R00212290/Desktop/Research Project/datasets/eeg/annotations_2017_C.csv')

