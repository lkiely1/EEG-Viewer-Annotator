
## used for summary annots from here: https://github.com/LockyWebb/NeonatalEEGArtefactDetection/tree/main
def annotations_convertor(filepath):
    for i in range(79):
        print(i + 1)
        with open(f"{filepath}/eeg{i + 1}_summary.txt", 'r') as file1:
            with open(f"{filepath}/converted/eeg{i + 1}.txt", 'w') as file2:
                first_line = file1.readline().split(',')
                file2.write(
                    "annotation_num,start,end,Fp1-F3,F3-C3,C3-P3,P3-O1,Fp2-F4,F4-C4,C4-P4,P4-O2,Fp1-F7,F7-T3,T3-T5,T5-O1,Fp2-F8,F8-T4,T4-T6,T6-O2,Fz-Cz,Cz-Pz")
                for line in file1:
                    if line != "":
                        annotation = line.strip('\n').split(',')
                        # print(annotation[20])
                        # 2 to 19 are channels
                        # read through each
                        channels = [0] * 18
                        for j in range(2, 20):
                            if int(annotation[j]) != 0:
                                annotation_num = annotation[j]
                                # print(annotation_num)
                                channels[j - 2] = 1
                        print(annotation_num)
                        print(channels)

                        start = annotation[20]
                        leng = annotation[21]
                        end = int(start) + int(leng)
                        print(f"{i},{start},{leng},{end}")

                        file2.write(f'{annotation_num},{start},{end}')
                        for k in range(len(channels)):
                            file2.write(f',{channels[k]}')
                        file2.write('\n')
        # next col


annotations_convertor('path to txt file')
