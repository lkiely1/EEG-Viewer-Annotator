from tkinter import *
from tkinter import filedialog

import pandas as pd
from tqdm import tk

from edf_to_csv import *

from plot_eeg import *


def retrieve():
    edf_to_csv(edf_file_path.get())
    # change csv file field to name of converted csv?


def get_channels():
    channels_indices = listbox.curselection()
    channels = []
    for index in channels_indices:
        channels.append(listbox.get(index))
    return channels


def load_csv():
    print("TEST")
    csv_data = pd.read_csv(csv_file_path.get())

    # need to clean header/column names (. in names causes problems, imagine will need more for other data)
    # e.g, clean_list = list of symbols to remove
    # for i in clean_list:
    # below line but '.' replaced with i so everything in list is removed from col names

    csv_data.columns = csv_data.columns.str.replace('.', '') # for cleaning

    col_list = list(csv_data.columns.values.tolist())

    # make plot options appear
    # make channel/plot options appear?

    listbox.delete(0, END)
    for i in range(len(col_list)):
        if i != 0:
            listbox.insert(i, col_list[i])


def plot_data():
    start = int(start_time.get())
    end = int(end_time.get())
    print(f"TEST - start {start}, end {end}")

    csv_data = pd.read_csv(csv_file_path.get())

    fig, axs = plot(csv_data, get_channels(), start, end)
    plt.show()


def edf_browse():
    path = filedialog.askopenfilename()
    edf_file_path.delete(0, END)  # Remove current text in entry
    edf_file_path.insert(0, path)

    csv_path = path.replace('.edf', '.csv')

    csv_file_path.delete(0, END)  # Remove current text in entry
    csv_file_path.insert(0, csv_path)
    return path


def csv_browse():
    path = filedialog.askopenfilename()
    csv_file_path.delete(0, END)  # Remove current text in entry
    csv_file_path.insert(0, path)
    return path


"""def on_time_change(*args): not working, will attempt again later
    start = start_time.get()
    end = end_time.get()
    amount = time_amount.get()

    new_start = amount - end
    new_end = start + amount
    new_amount = end - start

    start_time.delete(0, END)
    start_time.insert(0, new_start)

    end_time.delete(0, END)
    end_time.insert(0, new_end)

    time_amount.delete(0, END)
    time_amount.insert(0, new_amount)"""

root = Tk()
root.geometry("500x500")

file_frame = Frame(root)
file_frame.pack()

time_frame = Frame(root)
time_frame.pack()

# loading files, get way to verify filetype
edf_file_path = Entry(file_frame, width=20)
edf_file_path.insert(0, 'EDF File')
edf_file_path.pack(padx=5, pady=5)

edf_file_browse = Button(file_frame, text="Browse", command=edf_browse)
edf_file_browse.pack(padx=5, pady=5)

convert_button = Button(file_frame, text="Convert", command=retrieve)
convert_button.pack(padx=5, pady=5)

csv_file_path = Entry(file_frame, width=20)
csv_file_path.insert(0, edf_file_path.get())
csv_file_path.pack(padx=5, pady=5)

csv_file_browse = Button(file_frame, text="Browse", command=csv_browse)
csv_file_browse.pack(padx=5, pady=5)

load_csv_button = Button(file_frame, text="Load", command=load_csv)
load_csv_button.pack(padx=5, pady=5)


#time options (start end lenght) (changing 1 affects others)

label = Label(time_frame, text="Channels")
label.pack()

listbox = Listbox(time_frame, selectmode="multiple")
listbox.pack()

start_time = Entry(time_frame, width=20)
start_time.insert(0, 'start')
start_time.pack(padx=5, pady=5)


end_time = Entry(time_frame, width=20)
end_time.insert(0, 'end')
end_time.pack(padx=5, pady=5)


time_amount = Entry(time_frame, width=20)
time_amount.insert(0, 'amount')
time_amount.pack(padx=5, pady=5)


#plot button

plot_button = Button(time_frame, text="Plot", command=plot_data)
plot_button.pack(padx=5, pady=5)

#make plot appear

root.mainloop()
