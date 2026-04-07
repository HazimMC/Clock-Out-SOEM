import os
from datetime import datetime

Hour = 0
Minutes = 0
HalfDay_Flag = 1

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    enter = input("\n\n***********PRESS ENTER TO CONTINUE***********")

def set_time_if_pass_threshold(Time):

    global Hour, Minutes, HalfDay_Flag

    if Time < 730:
        Hour = 7
        Minutes = 30
    elif Time >= 730 and Time <= 930:
        return
    elif Time > 930 and Time < 1000:
        Hour = 9
        Minutes = 30
    elif Time < 1215:
        Hour = 7
        Minutes = 30
        HalfDay_Flag = 0
    elif Time >= 1215 and Time <= 1415:
        HalfDay_Flag = 0
        if Minutes < 45:
            Minutes += 60
            Hour -= 1

        Minutes = Minutes - 45
        Hour = Hour - 4
    elif Time > 1415:
        Hour = 9
        Minutes = 30
        HalfDay_Flag = 0

def get_hour_and_minute(clock_in):

    global Hour, Minutes

    clock_in = clock_in.strip()

    if len(clock_in) < 3:
        input("Please enter correct time. Press Enter to exit...")
        raise ValueError("Please enter correct time")

    if "." in clock_in:
        Hour, Minutes = clock_in.split(".", 1)
    elif ":" in clock_in:
        Hour, Minutes = clock_in.split(":", 1)
    else:                                   # if user enters 825 (8:25)
        if len(clock_in) == 4:
            Hour = clock_in[:2]
            Minutes = clock_in[2:]
        elif len(clock_in) == 3:
            Hour = clock_in[:1]
            Minutes = clock_in[1:]
        else:
            input("Please enter correct time. Press Enter to exit...")
            raise ValueError("Please enter correct time")

    #print("Minute: " + str(Minutes))
    #print("Hour: " + str(Hour))
    
    try:
        Hour = Hour.strip()
        Minutes = Minutes.strip().zfill(2)

        Combine_Time = int(Hour + Minutes)
        Hour = int(Hour)
        Minutes = int(Minutes)

        if Minutes > 59 or Hour > 23:
            raise ValueError("Wrong time format")
        
        set_time_if_pass_threshold(Combine_Time)

    except:
        input("Wrong time format. Press Enter to exit...")
        raise ValueError("Wrong time format")


def check_if_minute_is_over(hour, min):
    time_result = []

    while min >= 60:
        min -= 60
        hour += 1

    if min < 10:
        min = "0" + str(min)
    else:
        min = str(min)

    hour = str(hour)

    time_result.append(hour)
    time_result.append(min)

    return time_result

def ot_time_list(hour, min):

    ot_time = []
    first_time_flag = 1

    for i in range(1, 4):
        hour = hour + 1

        if first_time_flag == 1:
            min = min + 10
            first_time_flag = 0

        ot_time = check_if_minute_is_over(hour, min)

        print("OT of " + str(i) + " hour is at \t\t\t" + ot_time[0] + ":" + ot_time[1])

        new_min = min + 30

        ot_time = check_if_minute_is_over(hour, new_min)

        print("OT of " + str(i) + " hour and 30 minutes is at \t" + ot_time[0] + ":" + ot_time[1])

def pluralize(value, word):
    return f" {word} " if value == 1 else f" {word}s "

def check_time_left(hour, min):

    clock_out_hour = int(hour)
    clock_out_min = int(min)

    now = datetime.now()

    #print("\nCurrent Time: " + str(now.hour) + ":" + str(now.minute))

    now_total_min = now.hour * 60 + now.minute
    clock_out_total_min = clock_out_hour * 60 + clock_out_min

    if clock_out_total_min > now_total_min:

        diff_min = clock_out_total_min - now_total_min
        hour_left = diff_min // 60
        minute_left = diff_min % 60

        if minute_left == 60:
            minute_left = 0
            hour_left += 1

        message = "\nYou have "

        if hour_left != 0:
            message += str(hour_left) + pluralize(hour_left, "hour")
        if hour_left != 0 and minute_left != 0:
            message += "and "
        if minute_left != 0:
            message += str(minute_left) + pluralize(minute_left, "minute")
        
        message += "left for work today"

        print(message)

    else:
        print("\nIt is time to go home")

def main():

    #clear_screen()
    #print("Hazim (C) 2026. All rights reserved. \nCopyright Statement:\n\nThis software/firmware are \nprotected under relevant copyright laws")
    #pause()

    global Hour, Minutes, HalfDay_Flag
    now = datetime.now()

    clear_screen()

    date = (str(now.day) + "-" + str(now.month) + "-" + str(now.year))
    use_saved_time = False

    ### Check if clock in time is saved in file ###
    try:
        saved_clock_in = None
        with open("clock_in_time.txt", "r+") as f:
            for x in f:
                #print(f"DEBUG: The string is '{x}'")
                if date in x:
                    parts = x.strip().split(" ", 1)
                    if len(parts) == 2:
                        saved_clock_in = parts[1]

            if saved_clock_in is not None:
                clock_in = saved_clock_in
                use_saved_time = True
                print("Please enter your clock in time (ex: 08:30/24H Format): " + clock_in)
    except:
        pass

    if not use_saved_time:
        clock_in = (input("Please enter your clock in time (ex: 08:30/24H Format): "))

    get_hour_and_minute(clock_in)

    ### Half Day Time ###
    Half_Minutes = Minutes + 45
    Half_Hour = Hour + 4

    result_h = check_if_minute_is_over(Half_Hour, Half_Minutes)

    ### Normal Time ###

    print("")

    Minutes = Minutes + 30
    Hour = Hour + 9

    result = check_if_minute_is_over(Hour, Minutes)

    if HalfDay_Flag == 1 and int(now.hour) < 15:
        print("Half Day clock out time is at " + result_h[0] + ":" + result_h[1])

    print("Clock out time is at " + result[0] + ":" + result[1])

    ### Time left for work ###
    check_time_left(result[0], result[1])

    ### OT Time ###
    enable = input("\nList OT times? (y/n): ")
    if enable.lower() == 'y':
        ot_time_list(Hour, Minutes)
        pause()

    
    ### Save clock in time to file ###
    if not use_saved_time:
        with open("clock_in_time.txt", "a") as f:
            f.write(date + " " + clock_in + "\n")

if __name__ == "__main__":
    main()