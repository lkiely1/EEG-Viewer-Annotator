x = True
while x:
    with open('annotation_test_file.txt', 'a') as file:
        print("1) Background colour")
        print("2) Arrow")
        print("3) Line")
        mode = int(input("Which annotation type? -> "))
        if mode == 1:
            type = "bg"
            start_or_x = int(input("Enter the start time: "))
            end_or_y = int(input("Enter the end time: "))
            label = ""
        elif mode == 2:
            type = "arrow"
            start_or_x = int(input("Enter x value: "))
            end_or_y = int(input("Enter y value: "))
            label = str(input("Enter arrow label: "))
        elif mode == 3:
            type = "line"
            start_or_x = int(input("Enter x value for line: "))
            end_or_y = 0 # not needed
            label = ""
        else:
            print("Invalid input. Select 1) Background colour, 2) Arrow, 3)Line")
            continue

        file.write(f'{type},{start_or_x},{end_or_y},{label}')
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



