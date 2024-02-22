from tkinter import *

import pandas as pd

from edf_to_csv import *

from plot_csv_tk import *


def retrieve():
    edf_to_csv(my_entry.get())
    # change csv file field to name of converted csv?


def load_csv():
    print("TEST")
    csv_data = pd.read_csv(my_entry2.get() + '.csv')

    # need to clean header/column names (. in names causes problems, imagine will need more for other data)
    # e.g, clean_list = list of symbols to remove
    # for i in clean_list:
    # below line but '.' replaced with i so everything in list is removed from col names

    csv_data.columns = csv_data.columns.str.replace('.', '') # for cleaning

    col_list = list(csv_data.columns.values.tolist())

    # make plot options appear
    # make channel/plot options appear

    # list of channel names to select
    ### CHANGE TO UPDATE BOX NOT CREATE (NOT SURE HOW TO DO YET)
    label = Label(root, text="Channels")
    label.pack()

    listbox = Listbox(root)

    for i in range(len(col_list)):
        if i != 0:
            listbox.insert(i, col_list[i])

    listbox.pack()



root = Tk()
root.geometry("500x500")

frame = Frame(root)
frame.pack()

# loading files, get way to verify filetype
my_entry = Entry(frame, width=20)
my_entry.insert(0, 'filename') ### change to file select
my_entry.pack(padx=5, pady=5)

button = Button(frame, text="Convert", command=retrieve)
button.pack(padx=5, pady=5)

my_entry2 = Entry(frame, width=20)
my_entry2.insert(0, my_entry.get()) ### change to file select, if converted before get filename from that
my_entry2.pack(padx=5, pady=5)

button2 = Button(frame, text="Load", command=load_csv)
button2.pack(padx=5, pady=5)


#time options (start end lenght) (changing 1 affects others)

#plot button

#make plot appear

root.mainloop()
