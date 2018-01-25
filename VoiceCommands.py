import numpy
import time
import speech_recognition as sr
import pyttsx3 as ps
from bs4 import BeautifulSoup
import urllib3
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
from threading import Timer
import os

digits = "1234567890"

#The phrase you have to say to activate this
keyPhrase = "hey delta"

#Phrase said when the keyphrase is said
commandPhrase = "What do you need?"

#Speech recognizing stuff
recognizer = sr.Recognizer()
mic = sr.Microphone()

#Speaking engine
engine = ps.init()

#Set to true when the keyword is said
key_phrase_said = False

#This determines how many times the system asks for a command if one is not commandFound
checkCount = 2

#This is a list of all of the timer/reminders that have been set
timers = []
reminder_phrases = []

phraseSaid = ""

months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
weekdays = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
weekday_to_num = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}

class ReminderType:
    Reminder = 0
    Timer = 1
    Alarm = 2

class Reminder:

    def __init__(self, time, reminder_type, reminder_phrase="", does_repeat=False, repeat_days=[]):
        self.time = time
        self.reminder_type = reminder_type
        self.reminder_phrase = reminder_phrase
        self.does_repeat = does_repeat
        self.repeat_days = repeat_days

    def get_time(self):
        return self.time

    def get_reminder_phrase(self):
        return self.reminder_phrase

    def add_repeat(self, weekday):
        if type(weekday) is string:
            repeat_day = weekday_to_num[weekday]
            if not repeat_day in self.repeat_days:
                self.repeat_days.append(repeat_day)
        else:
            if not weekday in self.repeat_days:
                self.repeat_days.append(weekday)

#All of the commands
#Repeats whatever the person says
def repeat(phrase):
    if len(phrase) == 0:
        say("What do you want me to say?")
        phrase = listenForWord()
        print(phrase)
        say(phrase)
    else:
        print(phrase[4:len(phrase)])
        say(phrase[4:len(phrase)])

def getWeather(phrase):
    weather_url = "https://weather.com/weather/tenday/l/USMA0046:1:US"
    http_pool = urllib3.connection_from_url(weather_url)
    html = http_pool.urlopen('Get',weather_url)
    html = html.data

    weather_site = BeautifulSoup(html, "html.parser")

    day = 1
    if 'today' in phrase:
        day = 1
    elif 'tomorrow' in phrase:
        day = 2

    tableRows = weather_site.findAll('tr')

    infoList = tableRows[day].findAll('span')
    td = tableRows[day].findAll('td')

    day_of_week = infoList[0].contents[0]
    day = infoList[1].contents[0]
    weather = infoList[2].contents[0]
    high = infoList[3].contents[0]
    low = infoList[5].contents[0]
    precipitation_chance = infoList[8].contents[0]

    if 'temp' in phrase:
        say("The low is " + str(low) + " and the high is " + str(high))
        return None
    else:
        text = ""
        s_td = str(td)

        for i in range(s_td.find("title")+7,len(s_td)):
            if s_td[i] == "\"":
                break
            if s_td[i] == "F" and s_td[i-1] in digits:
                text = text + " degrees"
            else:
                text = text + s_td[i]
        print(text)
        say(text)
        return None

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

def convert_to_time(time):
    time_now = datetime.now()
    #The len(time) ensures that there were no seconds minutes or hours said
    if ":" in time or len(time) <= 3:
        hour_found = False
        hour = ""
        minute = "0"
        for l in time:
            #If a colon shows up it means thehour minute is done and it's time to look at minutes
            if l == ':':
                hour_found = True
            elif hour_found == False:
                hour = hour + l
            else:
                minute = minute + l
        print(hour)
        hour = hour.lstrip('0')
        print(hour)
        hour = int(hour)
        minute = minute.lstrip('0')
        if len(minute) != 0:
            minute = int(minute)
        else:
            minute = 0
        if "a.m" in time:
            if time == 12:
                hour = hour - 12
        elif hour != 12:
            hour = hour + 12

        timer_time = datetime(time_now.year, time_now.month, time_now.day, hour=hour, minute=minute)
        return timer_time

    else:
        t_phrase = tokenize(time)
        delta_seconds = 0
        delta_minutes = 0
        delta_hours = 0
        if "second" in time:
            for i in range(len(t_phrase)):
                if "second" in t_phrase[i]:
                    #The word right before second should be the correct number of seconds
                    delta_seconds = float(t_phrase[i-1])
        if "minute" in time:
            for i in range(len(t_phrase)):
                if "minute" in t_phrase[i]:
                    #The word right before second should be the correct number of seconds
                    delta_minutes = float(t_phrase[i-1])
        if "hour" in time:
            for i in range(len(t_phrase)):
                if "hour" in t_phrase[i]:
                    #The word right before second should be the correct number of seconds
                    delta_hours = float(t_phrase[i-1])

        #This code would calculate the reminder time by constantly checking to see
        #if the date had changed
        delta_time = timedelta(hours=delta_hours, minutes=delta_minutes, seconds=delta_seconds)
        end_time = time_now + delta_time
        return end_time

def set_alarm(phrase):
    print(digits)

    time_now = datetime.now()

    t_phrase = tokenize(phrase)
    times = []
    for t in t_phrase:
        for char in t:
            if char in digits:
                times.append(t)
                break

    print(len(times))
    print(times)
    for alarm_time in times:
        time = convert_to_time(alarm_time)
        print(time)
        timers.append(Reminder(time, ReminderType.Alarm, reminder_phrase="Ring ring ring your alarm is going off"))
        print(len(timers))

def set_reminder(phrase):
    global timers
    time_now = datetime.now()

    today_hour = time_now.hour
    today_minute = time_now.minute
    today_second = time_now.second

    #This analyzes the phrase to figure out how much time you want to set
    t_phrase = tokenize(phrase)

    if "at" in t_phrase:
        for i in range(len(t_phrase)):
            if t_phrase[i] == "at":
                number_start = i + 1

        end_time = convert_to_time(t_phrase[number_start])
        print(end_time)

        lower_bound_word = "to"
        upper_bound_word = "at"
    else:
        end_time = convert_to_time(phrase)
        print(end_time)

        lower_bound_word = "to"
        upper_bound_word = "in"

    #This analyzes the phrase to figure out what you want to be reminded of
    reminder_phrase = ""
    if "timer" in phrase:
        timers.append(Reminder(end_time, ReminderType.Timer, reminder_phrase="The timer is done"))
    else:
        lower_bound = 0
        upper_bound = 0
        if lower_bound_word in t_phrase:
            for i in range(len(t_phrase)):
                if t_phrase[i] == lower_bound_word:
                    lower_bound = i + 1
        if upper_bound_word in t_phrase:
            for i in range(len(t_phrase)):
                if t_phrase[i] == upper_bound_word:
                    upper_bound = i
        if upper_bound < lower_bound:
            for word in t_phrase[lower_bound:]:
                reminder_phrase = reminder_phrase + " " + word
            reminder_phrase = reminder_phrase + "."
            reminder_phrase = reminder_phrase.strip()
        else:
            for word in t_phrase[lower_bound:upper_bound]:
                reminder_phrase = reminder_phrase + " " + word
            reminder_phrase = reminder_phrase + "."
            reminder_phrase = reminder_phrase.strip()

        timers.append(Reminder(end_time, ReminderType.Reminder, reminder_phrase=reminder_phrase))

    print(reminder_phrase)

    if "timer" in phrase:
        say("Timer set")
    else:
        say("Reminder set")

def get_time_left(phrase):

    time_now = datetime.now()
    delta_time = timers[0].get_time() - time_now

    #In seconds
    time_left = delta_time.total_seconds()

    hours_left = int(time_left/3600)
    minutes_left = int((time_left - hours_left*3600)/(60))
    seconds_left = int(time_left - hours_left*3600 - minutes_left*60)

    print(hours_left)
    print(minutes_left)
    print(seconds_left)

    if hours_left == 0:
        if minutes_left == 0:
            say("There are " + str(seconds_left) + " seconds left.")
        elif minutes_left == 1:
            say("There is " + str(minutes_left) + " minute and " + str(seconds_left) + " seconds left.")
        else:
            say("There are " + str(minutes_left) + " minutes and " + str(seconds_left) + " seconds left.")
    elif hours_left == 1:
        say("There is 1 hour and " + str(minutes_left) + " minutes left.")
    else:
        say("There are " + str(hours_left) + " hours and " + str(minutes_left) + " minutes left.")


def remind(timer_num):
    print("Done")

    #The say command seems to break the entire system sometimes, it's unclear why
    say(timers[timer_num].get_reminder_phrase())

    #Remove the timer and the reminder phrase
    del timers[timer_num]
    print("Stuff removed")

def get_date(phrase):
    today_date = date.today().timetuple()

    month = months[today_date[1]]
    day = today_date[2]
    weekday = weekdays[today_date[6]]
    print("Today is " + str(weekday) + ", " + str(month) + " " + str(day))
    say("Today is " + str(weekday) + ", " + str(month) + " " + str(day))

def get_time(phrase):
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
    say("It is " + str(today_hour) + ":" + str(today_minute) + " " + str(time_of_day))

def exit_program(phrase):
    os._exit(1)

commands = {"say": repeat, "weather": getWeather, "temp": getWeather, "remind": set_reminder, "timer": set_reminder, "alarm":set_alarm, "left": get_time_left, "time": get_time, "date": get_date, "exit": exit_program}

def say(phrase):
    engine.say(phrase)
    engine.runAndWait()

def listenForWord():
    with mic as source:
        print("Request")
        audio = recognizer.listen(source)

    #Processes the audio
    print("Processing")
    try:
        words = recognizer.recognize_google(audio)
        print(words)
        return words
    except sr.UnknownValueError:
        print("Got nothing")
        return ""
    except sr.RequestError:
        print("Didn't work")
        return ""

def listen_for_command(command):
    count = 0
    print(command)
    while True:
        if count > checkCount:
            break

        commandFound = False
        for commandKey in list(commands.keys()):
            #If the key is somewhere in the command extract the command key and just leave the information
            if commandKey in command:
                print("Command: " + commandKey)
                #This clears the command word and only leaves what is said after
                #words = command[command.find(commandKey):len(command)]

                #This just takes the whole thing instead
                words = command

                #Gets rid of all of the extra spaces before and after the word
                words = words.strip()

                #Calls whatever command is in the dictionary of commands
                commands[commandKey](words)
                commandFound = True
                break
        if commandFound == False:
            if count != 0:
                say("Command not found")
            say(commandPhrase)
            command = listenForWord()
            count = count + 1
        else:
            break

def callback(recognizer, audio):
    global key_phrase_said
    global phraseSaid

    print("Processing...")
    try:
        s = recognizer.recognize_google(audio)
        s = s.lower()
        print("You said: " + s)

        #Listens for the specific keyphrase
        if keyPhrase in s:
            #This gets a string of everything said after the key phrase was said
            phraseSaid = s[s.find(keyPhrase)+len(keyPhrase):]
            key_phrase_said = True
            print("Key phrase said")

    except sr.UnknownValueError:
        print("Got nothing")
    except sr.RequestError:
        print("Didn't work")

with mic as source:
    recognizer.adjust_for_ambient_noise(source)

#Starts listening but creates a function that can stop the listening
print("Starting...")
stop_listening = recognizer.listen_in_background(mic, callback)
print("Ready")

while True:
    if key_phrase_said == True:
        stop_listening(wait_for_stop=True)
        listen_for_command(phraseSaid)
        key_phrase_said = False
        stop_listening = recognizer.listen_in_background(mic, callback)
    if len(timers) != 0:
        for i in range(len(timers)):
            #Timers contain the start and end dates
            if datetime.now() >= timers[i].get_time():
                stop_listening(wait_for_stop=True)
                remind(i)
                stop_listening = recognizer.listen_in_background(mic, callback)
                break

#Stops the listening
stop_listening(wait_for_stop=True)
print("Doneeeeeeeeeee")
