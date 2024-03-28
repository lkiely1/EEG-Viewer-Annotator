import mne


def edf_to_csv(filename):
    if filename.endswith('.edf'):
        filename = filename.replace('.edf', '')
        data_raw_file = (filename+'.edf')
        annot = mne.read_annotations(data_raw_file) # annots  shown in debug

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


