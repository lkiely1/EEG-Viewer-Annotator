
# EEG Viewer and Annotatior

PyQt5 based application for plotting and annotating EEG data.

Developed as part of research project at MTU

# Features

Load edf file: User selects EDF file to load using filepicker
![load-1.png](/readme_assets/load-1.png)
![load-2.png](/readme_assets/load-2.png)

Choose channels: User can select 1 or all channels from list box
![channels.png](/readme_assets/channels.png)

Set time: User can set the start + end time and duration (Start and end required, end calculated by setting start and duration)
![time.png](/readme_assets/time.png)

Load/preview annotations and change annotation directory: Seperate window can be opened to select annotation file to load, change directory of where user created annotations are stored/loaded from, preview annotations from both files
![annot-load-1.png](/readme_assets/annot-load-1.png)
![annot-load-2.png](/readme_assets/annot-load-2.png)

Plot data: matplotlib plot of data 
![plot.png](/readme_assets/plot.png)

Move timeline to view data in dataset (click and drag mouse over bottom timeline subplot)

Create annotation by clicking and dragging over area on plot
![create-annot.png](/readme_assets/create-annot.png)

# Usage

Run main.py

1) Select EDF file to load

2) Choose channel(s) to plot, set start and end time

3(optional) Select annotation file to load

4) Plot the data and view

5) Plot interaction: click and drag on timeline subplot to move data shown on above subplots, click and drag on above subplots to draw annotation

6) Edit, save or cancel created annotation, set annotation type, change start/end times if needed

# Installation

Python 3.12

Dependencies listed in `requrements.txt`, use `pip install -r requirements.txt`

May need to install MNE tools or PyQt5 manually:

mnetools: https://mne.tools/stable/install/index.html

PyQt5:
https://pypi.org/project/PyQt5/

# Converting annotations into compatible format

There are 2 included .py scripts for converting annotations in different format to compatible format

Format used: rows of `annot_num, start, end` stored in txt file

`annot_num` corresponds to a type of annotation (e.g. 7 = Seizure)

Used annotation types: Clean EEG, Device Interference, EMG, Movement, Electrode, HF ventilation, Biological Rhythm, Seizure (represented by 0 - 7)

If you need to load annotations from another format, create a script that converts them into this format

`csv_annotations_convertor.py` is used for csv files found in this dataset: https://zenodo.org/records/4940267

`artefact_bipolar_annots_convertor.py` used for annotations found here: https://github.com/LockyWebb/NeonatalEEGArtefactDetection/tree/main

# Other

Currently has memory leak issue if you load multiple EDF files or plot multiple times without restarting application 

Bipolar channel conversion only tested with this dataset: https://zenodo.org/records/4940267

This can be disabled if needed

Other bugs may be present




