import mne

# this is no longer needed. early in project was converting EDF data into CSV files. However, this isn't needed as
# edf files can be read as pandas dataframes anyway
# ignore this


def edf_to_csv(filename):
    if filename.endswith('.edf'):
        filename = filename.replace('.edf', '')
        data_raw_file = (filename+'.edf')
        annot = mne.read_annotations(data_raw_file)  # shows annotations if they exist, shown in debug

        raw = mne.io.read_raw_edf(data_raw_file)

        df = raw.to_data_frame()
        df.to_csv(filename + '.csv', index=False)

        sfreq = raw.info['sfreq']

        with open(filename + '_info.txt', 'w') as f:
            f.write(str(sfreq))
        f.close()
    else:
        print('Not a .edf file')
    print("Complete")
