x = True
while x:
    with open('annotation_test_file.txt', 'a') as file:
        print("1) Background colour")
        print("2) Arrow")
        print("3) Line")
        print("4) Box")
        print("5) Bar")
        mode = int(input("Which annotation type? -> "))
        if mode == 1:
            annotation_type = "bg"
            annotation_x = int(input("Enter the start time: "))
            end_time = int(input("Enter the end time: "))
            annotation_x2 = annotation_x + end_time
            annotation_y = 0 # not needed
            label = str(input("Enter background label: "))
        elif mode == 2:
            annotation_type = "arrow"
            annotation_x = int(input("Enter x value: "))
            annotation_y = int(input("Enter y value: "))
            label = str(input("Enter arrow label: "))
            annotation_x2 = 0 # not needed
        elif mode == 3:
            annotation_type = "line"
            annotation_x = int(input("Enter x value for line: "))
            annotation_x2 = 0 # not needed
            annotation_y = 0 # not needed
            label = str(input("Enter line label: "))
        elif mode == 4:
            annotation_type = "box"
            annotation_x = int(input("Enter start x value for box: "))
            annotation_x2 = int(input("Enter end x value for box: "))
            annotation_y = int(input("Enter y value for box: ")) # could change to something else? if should be pre defined?
            label = str(input("Enter box label: "))
        elif mode == 5:
            annotation_type = "bar"
            annotation_x = int(input("Enter start x value for bar: "))
            annotation_x2 = int(input("Enter end x value for bar: "))
            annotation_y = 0 # should be under line, could calc where in plot_csv
            label = str(input("Enter box label: "))
        else:
            print("Invalid input. Select 1) Background colour, 2) Arrow, 3)Line")
            continue

        file.write(f'{annotation_type},{annotation_x},{annotation_x2},{annotation_y},{label}')
        file.write('\n')

        continue_program = 'a'
        while continue_program.lower() != 'y' or continue_program.lower() != 'n':
            continue_program = input("Do you want to add another? (y/n) ")
            if continue_program.lower() == 'y':
                break
            elif continue_program.lower() == 'n':
                file.close()
                x = False
                break
            else:
                print("Invalid input. Please enter y or n")



