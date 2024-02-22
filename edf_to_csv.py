import mne

def edf_to_csv(filename):
    if filename.endswith('.edf'):
        data_raw_file = (filename)
        raw = mne.io.read_raw_edf(data_raw_file)
        df = raw.to_data_frame()
        df.to_csv(filename + '.csv', index=False)

        sfreq = raw.info['sfreq']

        with open(filename + '_info.txt', 'w') as f:
            f.write(str(sfreq))
        f.close()
    else:
        print('Not a .edf file')


#edf_to_csv('S001R01.edf')
