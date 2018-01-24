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

#The phrase you have to say to activate this
keyPhrase = "hey carl"

#Phrase said when the keyphrase is said
commandPhrase = "What do you need?"

recognizer = sr.Recognizer()
mic = sr.Microphone()
engine = ps.init()

#Set to true when the keyword is said
key_phrase_said = False

#This determines how many times the system asks for a command if one is not commandFound
checkCount = 2

#This is a list of all of the timer/reminders that have been set
timers = []
start_times = []
reminder_phrases = []

phraseSaid = ""

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
            else:
                text = text + s_td[i]
        print(text)
        say(text)
        return None

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
            if "hour" in t_phrase[i]:
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
            for word in t_phrase[lower_bound:]:
                reminder_phrase = reminder_phrase + " " + word
            reminder_phrase = reminder_phrase + "."
            reminder_phrase = reminder_phrase.strip()
        else:
            for word in t_phrase[lower_bound:upper_bound]:
                reminder_phrase = reminder_phrase + " " + word
            reminder_phrase = reminder_phrase + "."
            reminder_phrase = reminder_phrase.strip()
    #This code would calculate the reminder time by constantly checking to see
    #if the date had changed
    '''
    delta_time = timedelta(hours=delta_hours, minutes=delta_minutes, seconds=delta_seconds)
    end_time = time_now + delta_time
    print(str(time_now) + " | " + str(end_time))
    '''

    #Change in time in seconds
    delta_time = delta_seconds + delta_minutes*60 + delta_hours*3600
    print(delta_time)
    #Adds and starts the most recent timer added, which is this one
    timers.append(Timer(delta_time, remind))
    timers[len(timers)-1].start()

    start_times.append(time.time())
    reminder_phrases.append(reminder_phrase)

    print(reminder_phrase)

    if "timer" in phrase:
        say("Timer set")
    else:
        say("Reminder set")

def get_time_left(phrase):
    time_left = timers[0].interval - (time.time() - start_times[0])

    hours_left = int(time_left/3600)
    minutes_left = int((time_left - hours_left*3600)/(60))
    seconds_left = int(time_left - hours_left*3600 - minutes_left*60)
    print(timers[0].interval)
    print(time.time())
    print(start_times[0])
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


def remind():
    print("Done")
    say(reminder_phrases[0])

    #Remove the timer and the reminder phrase
    del reminder_phrases[0]
    del timers[0]

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

commands = {"say": repeat, "weather": getWeather, "temp": getWeather, "remind": set_reminder, "timer": set_reminder, "left": get_time_left, "time": get_time, "date": get_date, "exit": exit_program}

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

#Stops the listening
#stop_listening(wait_for_stop=True)
print("Done")
