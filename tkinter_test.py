from tkinter import *

import pandas as pd

from edf_to_csv import *

from plot_csv_tk import *


def retrieve():
    edf_to_csv(edf_file_path.get())
    # change csv file field to name of converted csv?


def load_csv():
    print("TEST")
    csv_data = pd.read_csv(csv_file_path.get() + '.csv')

    # need to clean header/column names (. in names causes problems, imagine will need more for other data)
    # e.g, clean_list = list of symbols to remove
    # for i in clean_list:
    # below line but '.' replaced with i so everything in list is removed from col names

    csv_data.columns = csv_data.columns.str.replace('.', '') # for cleaning

    col_list = list(csv_data.columns.values.tolist())

    # make plot options appear
    # make channel/plot options appear

    listbox.delete(0, END)
    for i in range(len(col_list)):
        if i != 0:
            listbox.insert(i, col_list[i])


def plot():
    start = start_time.get()
    end = end_time.get()
    print(f"TEST - start {start}, end {end}")




root = Tk()
root.geometry("500x500")

frame = Frame(root)
frame.pack()

# loading files, get way to verify filetype
edf_file_path = Entry(frame, width=20)
edf_file_path.insert(0, 'filename') ### change to file select
edf_file_path.pack(padx=5, pady=5)

convert_button = Button(frame, text="Convert", command=retrieve)
convert_button.pack(padx=5, pady=5)

csv_file_path = Entry(frame, width=20)
csv_file_path.insert(0, edf_file_path.get()) ### change to file select, if converted before get filename from that
csv_file_path.pack(padx=5, pady=5)

load_csv_button = Button(frame, text="Load", command=load_csv)
load_csv_button.pack(padx=5, pady=5)


#time options (start end lenght) (changing 1 affects others)

label = Label(root, text="Channels")
label.pack()

listbox = Listbox(root)
listbox.pack() ## not at top for some reason??

start_time = Entry(frame, width=20)
start_time.insert(0, 'start')
start_time.pack(padx=5, pady=5)

end_time = Entry(frame, width=20)
end_time.insert(0, 'end')
end_time.pack(padx=5, pady=5)

time_amount = Entry(frame, width=20)
time_amount.insert(0, 'amount')
time_amount.pack(padx=5, pady=5)

#plot button

plot_button = Button(frame, text="Plot (not working)", command=plot)
plot_button.pack(padx=5, pady=5)

#make plot appear

root.mainloop()
