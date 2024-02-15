import mne


def edf_to_csv(filename): # way to make sure file is edf to prevent crash?
    if filename.endswith('.edf'):
        filename = filename.replace('.edf', '')
    data_raw_file = (filename + '.edf')
    raw = mne.io.read_raw_edf(data_raw_file)
    df = raw.to_data_frame()
    df.to_csv(filename + '.csv', index=False)


edf_to_csv('S001R01.edf')
