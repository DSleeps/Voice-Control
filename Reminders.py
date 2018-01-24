import time
from datetime import datetime
from datetime import date
from datetime import timedelta
from threading import Timer

months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
weekdays = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}

#Separates each word from eachother and puts them in a list
def tokenize(input_string):
    tokenized = []
    temp = ''
    for l in input_string:
        if l != ' ':
            temp = temp + l
        else:
            tokenized.append(temp)
            temp = ''
    tokenized.append(temp)
    return tokenized

def set_reminder(phrase):
    time_now = datetime.now()

    today_hour = time_now.hour
    today_minute = time_now.minute
    today_second = time_now.second

    #This analyzes the phrase to figure out how much time you want to set
    t_phrase = tokenize(phrase)
    delta_seconds = 0
    delta_minutes = 0
    delta_hours = 0
    if "second" in phrase:
        for i in range(len(t_phrase)):
            if "second" in t_phrase[i]:
                #The word right before second should be the correct number of seconds
                delta_seconds = float(t_phrase[i-1])
    if "minute" in phrase:
        for i in range(len(t_phrase)):
            if "minute" in t_phrase[i]:
                #The word right before second should be the correct number of seconds
                delta_minutes = float(t_phrase[i-1])
    if "hour" in phrase:
        for i in range(len(t_phrase)):
            if "minute" in t_phrase[i]:
                #The word right before second should be the correct number of seconds
                delta_hours = float(t_phrase[i-1])

    #This analyzes the phrase to figure out what you want to be reminded of
    reminder_phrase = ""
    if "timer" in phrase:
        reminder_phrase = "The timer is done"
    else:
        lower_bound = 0
        upper_bound = 0
        if "to" in t_phrase:
            for i in range(len(t_phrase)):
                if t_phrase[i] == "to":
                    lower_bound = i + 1
        if "in" in t_phrase:
            for i in range(len(t_phrase)):
                if t_phrase[i] == "in":
                    upper_bound = i
        if upper_bound < lower_bound:
            print(upper_bound)
            reminder_phrase = t_phrase[lower_bound:]
        else:
            for word in t_phrase[lower_bound:upper_bound]:
                reminder_phrase = reminder_phrase + " " + word
            reminder_phrase = reminder_phrase + "."
            reminder_phrase = reminder_phrase.strip()

    delta_time = timedelta(hours=delta_hours, minutes=delta_minutes, seconds=delta_seconds)
    end_time = time_now + delta_time
    print(str(time_now) + " | " + str(end_time))
    print(reminder_phrase)

def get_date():
    today_date = date.today().timetuple()

    month = months[today_date[1]]
    day = today_date[2]
    weekday = weekdays[today_date[6]]
    print("Today is " + str(weekday) + ", " + str(month) + " " + str(day))

def get_time():
    date_and_time = datetime.now()

    today_hour = date_and_time.hour
    today_minute = date_and_time.minute
    today_second = date_and_time.second

    if today_hour >= 12:
        time_of_day = "pm"
    else:
        time_of_day = "am"

    #These adjust military time to regular time
    if today_hour > 12:
        today_hour = today_hour - 12
    elif today_hour == 0:
        today_hour = 12

    print("It is " + str(today_hour) + ":" + str(today_minute) + " " + str(time_of_day))
