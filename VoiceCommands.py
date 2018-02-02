from __future__ import print_function
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
import random

#All of the Google Calendar Imports
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

digits = "1234567890"

today = date.today()
tomorrow = today + timedelta(days=1)

#Machine Operated Neurological Technological Enhancement
#The phrase you have to say to activate this
keyPhrase1 = "hey adam"
keyPhrase2 = "hey atom"

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

#The number of seconds a phrase said to A.T.O.M. can be
max_seconds = 8

#This is a list of all of the timer/reminders that have been set
timers = []
reminder_phrases = []

phraseSaid = ""

months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
weekdays = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
weekday_to_num = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
month_names = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}

alarms = {0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[]}

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
        self.is_silenced = False

    def get_time(self):
        return self.time

    def get_reminder_phrase(self):
        return self.reminder_phrase

    def get_days(self):
        return self.repeat_days

    def get_type(self):
        return self.reminder_type

    def is_silent(self):
        return self.is_silenced

    def is_repeating(self):
        return self.does_repeat

    def add_day(self, weekday):
        if type(weekday) is type('string'):
            repeat_day = weekday_to_num[weekday]
            if not repeat_day in self.repeat_days:
                self.repeat_days.append(repeat_day)
        else:
            if not weekday in self.repeat_days:
                self.repeat_days.append(weekday)

    def set_time(new_time):
        self.time = new_time

    def set_repeat(self, is_repeat):
        self.does_repeat = is_repeat

    def set_silence(self, silence):
        self.is_silenced = silence

#All of the commands
#Repeats whatever the person says
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

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

def convert_to_time(time, time_start=datetime.now()):
    #The len(time) ensures that there were no seconds minutes or hours said
    if ":" in time or (not "hour" in time and not "minute" in time and not "second" in time):
        hour_found = False
        hour = ""
        minute = "0"
        for l in time:
            #If a colon shows up it means thehour minute is done and it's time to look at minutes
            if l == ':':
                hour_found = True
            elif l == ' ':
                break
            elif hour_found == False:
                hour = hour + l
            else:
                minute = minute + l

        hour = hour.lstrip('0')
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

        timer_time = datetime(time_start.year, time_start.month, time_start.day, hour=hour, minute=minute)
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
        end_time = time_start + delta_time
        return end_time

def set_alarm(phrase):
    time_now = datetime.now()

    if "cancel" in phrase or "silen" in phrase:
        if "today" in phrase:
            if "cancel" in phrase:
                alarms[time_now.weekday()] = []
                #Also have to remove all of the alarms from the timers
                for timer in timers:
                    if timer.get_type() == ReminderType.Alarm:
                        timers.remove(timer)
            else:
                for alarm in alarms[time_now.weekday()]:
                    alarm.set_silence(True)
        elif "tomorrow" in phrase:
            weekday = time_now.weekday() + 1
            if weekday >= 7:
                weekday += -7
            if "cancel" in phrase:
                alarms[weekday] = []
            else:
                for alarm in alarms[weekday]:
                    alarm.set_silence(True)
        else:
            for weekday in list(weekday_to_num.keys()):
                if weekday in phrase:
                    #Removes all of the alarms from the list
                    if "cancel" in phrase:
                        alarms[weekday_to_num[weekday]] = []
                    else:
                        for alarm in alarms[weekday_to_num[weekday]]:
                            alarm.set_silence(True)
        print(alarms)
        if "cancel" in phrase:
            say("Alarms canceled")
        else:
            say("Alarms silenced")

    else:
        t_phrase = tokenize(phrase)
        times = []
        for t in t_phrase:
            for char in t:
                if char in digits:
                    #This checks if a.m. or p.m. was said after the time was mentioned, and if it was add it to the time
                    if t_phrase.index(t)+1 < len(t_phrase):
                        if t_phrase[t_phrase.index(t)+1][0] in digits:
                            times.append(t)
                        else:
                            times.append(t + " " + t_phrase[t_phrase.index(t)+1])
                    else:
                        times.append(t)
                    break

        new_reminders = []
        print(times)
        for alarm_time in times:
            time = convert_to_time(alarm_time)
            new_reminders.append(Reminder(time, ReminderType.Alarm, reminder_phrase="Ring ring it's an alarm"))
            print(time)

        weekday_said = False
        for key in list(weekday_to_num.keys()):
            if key in phrase:
                weekday_said = True
                for reminder in new_reminders:
                    reminder.add_day(weekday_to_num[key])

        if "repeat" in phrase or "every" in phrase:
            for reminder in new_reminders:
                reminder.set_repeat(True)

        for reminder in new_reminders:
            for day in reminder.get_days():
                alarms[day].append(reminder)

        print(alarms)

        #If no weekday is said add the alarms to the immediate timer
        if weekday_said == False:
            for reminder in new_reminders:
                timers.append(reminder)
                print(len(timers))
        else:
            #If a weekday is specified check if it is today
            for reminder in new_reminders:
                for weekday in reminder.get_days():
                    #If it is today and the time hasn't passed yet, set it to today's alarms
                    if weekday == time_now.weekday() and time_now < reminder.get_time():
                        print("Added to today's timer")
                        timers.append(reminder)

        if len(new_reminders) > 1:
            say("Alarms set")
        else:
            say("Alarm set")

def set_reminder(phrase):
    global timers
    time_now = datetime.now()

    today_hour = time_now.hour
    today_minute = time_now.minute
    today_second = time_now.second

    #This analyzes the phrase to figure out how much time you want to set
    t_phrase = tokenize(phrase)

    if "cancel" in phrase:
        if "remind" in phrase:
            for timer in timers:
                if timer.get_type() == ReminderType.Reminder:
                    timers.remove(timer)
            say("Reminders cancelled")
        else:
            for timer in timers:
                if timer.get_type() == ReminderType.Timer:
                    timers.remove(timer)
            say("Timers cancelled")
    else:
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
    r = timers[timer_num]

    if r.get_type() == ReminderType.Alarm and r.is_repeating() == False:
        now = datetime.now()
        alarms[now.weekday()].remove(r)
        print("Alarm removed")
        print(alarms)

    #Remove the timer and the reminder phrase
    del timers[timer_num]
    print("Stuff removed")

def get_events(phrase):
    event_phrase_initial = phrase
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    start_time = datetime.now()
    end_time = start_time + timedelta(days=2)
    end_time = end_time.replace(hour=0,minute=0,second=0,microsecond=0)

    calendars = service.calendarList().list().execute()
    calendar_ids = []
    for calendar in calendars["items"]:
        calendar_ids.append(calendar.get('id'))
        print(calendar.get('id'))

    #This while loop handles getting the date
    event_phrase = event_phrase_initial
    while True:
        t_phrase = tokenize(event_phrase)
        if "today" in event_phrase:
            break
        elif "tomorrow" in event_phrase:
            one_day = timedelta(days=1)
            start_time = start_time + one_day
            end_time = end_time + one_day
            break
        elif "on" in t_phrase:
            for month in list(month_names.keys()):
                if month in event_phrase:
                    event_month = month_names[month]
                    break

            t_phrase = tokenize(event_phrase[event_phrase.index("on"):])
            event_day = ""
            for word in t_phrase:
                if event_day != "":
                    break
                for d in digits:
                    if d in word:
                        for i in word:
                            if i in digits:
                                event_day = str(event_day) + str(i)
                        event_day = int(event_day)
                        break
            print("Day: " + str(event_day))
            print("Month: " + str(event_month))
            start_time = start_time.replace(month=event_month, day=event_day)
            end_time = end_time.replace(month=event_month, day=event_day)
            print("Start: " + str(start_time))
            print("End: " + str(end_time))
            break
        elif "week" in t_phrase:
            start_time = start_time + timedelta(weeks=1)
            end_time = end_time + timedelta(weeks=1)
            break
        elif "weeks" in t_phrase:
            num_of_weeks = int(t_phrase[t_phrase.index("weeks")-1])
            start_time = start_time + timedelta(weeks=num_of_weeks)
            end_time = end_time + timedelta(weeks=num_of_weeks)
            break
        elif "day" in t_phrase:
            start_time = start_time + timedelta(days=1)
            end_time = end_time + timedelta(days=1)
            break
        elif "days" in t_phrase:
            num_of_days = int(t_phrase[t_phrase.index("days")-1])
            start_time = start_time + timedelta(weeks=num_of_days)
            end_time = end_time + timedelta(weeks=num_of_days)
            break
        else:
            weekday_num = -1
            for weekday in weekday_to_num:
                if weekday in event_phrase:
                    weekday_num = weekday_to_num[weekday]
            if weekday_num != -1:
                next_week = False
                if "next" in event_phrase:
                    next_week = True

                first = True
                in_next_week = False
                next_day = datetime.now()
                while True:
                    next_day = next_day + timedelta(days=1)
                    print(next_day.weekday())
                    print(weekday_num)
                    print(next_day)
                    if next_day.weekday() == 0 and first == False:
                        in_next_week = True
                    if next_day.weekday() == weekday_num:
                        if next_week == False:
                            start_time = start_time.replace(year=next_day.year, month=next_day.month, day=next_day.day)
                            end_time = end_time.replace(year=next_day.year, month=next_day.month, day=next_day.day)
                            break
                        elif in_next_week == True and next_week == True:
                            start_time = start_time.replace(year=next_day.year, month=next_day.month, day=next_day.day)
                            end_time = end_time.replace(year=next_day.year, month=next_day.month, day=next_day.day)
                            break
                    first = False
                break
            else:
                say("What do you want to know the events of?")
                event_phrase = listenForWord()

                #This ensures that if the person doesn't say on when they mention a specific date it still recognizes it
                t_event_phrase = tokenize(event_phrase)
                if t_event_phrase[0] in list(month_names.keys()):
                    event_phrase = "on " + event_phrase

    if not "today" in event_phrase:
        print("No today")
        start_time = start_time.replace(hour=0, minute=0,second=0,microsecond=0)

    #Only want the events for a single day
    #Has to be two days to include the events that overlap into the next day
    end_time = start_time + timedelta(days=2)
    end_time = end_time.replace(hour=0, minute=0,second=0,microsecond=0)

    print('Getting the upcoming events ' + str(start_time.isoformat() + 'Z') + " | " + str(end_time.isoformat() + 'Z'))

    events = []
    for calendar_id in calendar_ids:
        eventsResult = service.events().list(
            calendarId=calendar_id, timeMin=start_time.isoformat() + 'Z', timeMax=end_time.isoformat() + 'Z', maxResults=20, singleEvents=True,
            orderBy='startTime').execute()
        events = events + eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    event_dict = {}
    num_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        #This filters out the events that don't start on the right day
        start_day = start[8:10]
        start_day = start_day.lstrip('0')
        if str(start_day) == str(start_time.day):
            num = float(start[11:13] + "." + start[14:16])
            num_list.append(num)
            event_dict[num] = event

    num_list.sort()
    for num in num_list:
        start = event_dict[num]['start'].get('dateTime', event['start'].get('date'))
        end = event_dict[num]['end'].get('dateTime', event['end'].get('date'))
        #This filters out the events that don't start on the right day
        start_day = start[8:10]
        start_day = start_day.lstrip('0')
        if str(start_day) == str(start_time.day):
            print(start, event_dict[num]['summary'])
            print(event_dict[num]['summary'] + " that goes from " + start[11:13] + " " + start[14:16] + " to " + end[11:13] + " " + end[14:16] + ". ")
            say(event_dict[num]['summary'] + " that goes from " + start[11:13] + " " + start[14:16] + " to " + end[11:13] + " " + end[14:16] + ". ")

def set_event(phrase):

    say("What would you like the event to be?")
    event_phrase_initial = listenForWord()

    #The while loop handles getting the type of the event
    event_phrase = event_phrase_initial
    while True:
        if "event" in event_phrase:
            event_type = "event"
            break
        elif "reminder" in event_phrase:
            event_type = "reminder"
            break
        say("Is it an event or a reminder?")
        event_phrase = listenForWord()
        #Listen for new info

    #This while loop handles getting the start and end time of the event
    event_phrase = event_phrase_initial
    while True:
        t_phrase = tokenize(event_phrase)
        times = []
        for word in t_phrase:
            if ":" in word:
                times.append(word)

        if len(times) == 0:
            if "from" in t_phrase:
                check_times = t_phrase[t_phrase.index("from")+1:t_phrase.index("from")+7] + [""]
                possible_times = []
                print(len(check_times))
                for i in range(len(check_times)):
                    for d in digits:
                        if d in check_times[i]:
                            possible_times.append(check_times[i] + " " + check_times[i+1])

                print(possible_times[0])
                print(possible_times[1])

                if len(possible_times) > 1:
                    start_time = convert_to_time(possible_times[0])
                    end_time = convert_to_time(possible_times[1], time_start=start_time)
                    break
        elif len(times) == 1:
            #The other part is to make sure we get the a.m. or p.m. part of the times
            start_time = convert_to_time(str(times[0]) + " " + t_phrase[t_phrase.index(times[0]) + 1])
            end_time = convert_to_time(event_phrase[event_phrase.index(times[0])+len(times[0]):], time_start=start_time)
            break
        elif len(times) == 2:
            start_time = convert_to_time(str(times[0]) + " " + t_phrase[t_phrase.index(times[0]) + 1])
            end_time = convert_to_time(str(times[1]) + " " + t_phrase[t_phrase.index(times[1]) + 1])
            break
        say("What is the start and end time?")
        event_phrase = listenForWord()
        #Listen for new info

    #This while loop handles getting the date
    event_phrase = event_phrase_initial
    while True:
        t_phrase = tokenize(event_phrase)
        if "today" in event_phrase:
            break
        elif "tomorrow" in event_phrase:
            one_day = timedelta(days=1)
            start_time = start_time + one_day
            end_time = end_time + one_day
            break
        elif "on" in t_phrase:
            for month in list(month_names.keys()):
                if month in event_phrase:
                    event_month = month_names[month]
                    break

            t_phrase = tokenize(event_phrase[event_phrase.index("on"):])
            event_day = ""
            for word in t_phrase:
                if event_day != "":
                    break
                for d in digits:
                    if d in word:
                        for i in word:
                            if i in digits:
                                event_day = str(event_day) + str(i)
                        event_day = int(event_day)
                        break
            print("Day: " + str(event_day))
            print("Month: " + str(event_month))
            start_time = start_time.replace(month=event_month, day=event_day)
            end_time = end_time.replace(month=event_month, day=event_day)
            print("Start: " + str(start_time))
            print("End: " + str(end_time))
            break
        elif "week" in t_phrase:
            start_time = start_time + timedelta(weeks=1)
            end_time = end_time + timedelta(weeks=1)
            break
        elif "weeks" in t_phrase:
            num_of_weeks = int(t_phrase[t_phrase.index("weeks")-1])
            start_time = start_time + timedelta(weeks=num_of_weeks)
            end_time = end_time + timedelta(weeks=num_of_weeks)
            break
        elif "day" in t_phrase:
            start_time = start_time + timedelta(days=1)
            end_time = end_time + timedelta(days=1)
            break
        elif "days" in t_phrase:
            num_of_days = int(t_phrase[t_phrase.index("days")-1])
            start_time = start_time + timedelta(weeks=num_of_days)
            end_time = end_time + timedelta(weeks=num_of_days)
            break
        else:
            weekday_num = -1
            for weekday in weekday_to_num:
                if weekday in event_phrase:
                    weekday_num = weekday_to_num[weekday]
            if weekday_num != -1:
                next_week = False
                if "next" in event_phrase:
                    next_week = True

                first = True
                in_next_week = False
                next_day = datetime.now()
                while True:
                    next_day = next_day + timedelta(days=1)
                    print(next_day.weekday())
                    print(weekday_num)
                    print(next_day)
                    if next_day.weekday() == 0 and first == False:
                        in_next_week = True
                    if next_day.weekday() == weekday_num:
                        if next_week == False:
                            start_time = start_time.replace(year=next_day.year, month=next_day.month, day=next_day.day)
                            end_time = end_time.replace(year=next_day.year, month=next_day.month, day=next_day.day)
                            break
                        elif in_next_week == True and next_week == True:
                            start_time = start_time.replace(year=next_day.year, month=next_day.month, day=next_day.day)
                            end_time = end_time.replace(year=next_day.year, month=next_day.month, day=next_day.day)
                            break
                    first = False
                break
            else:
                say("What day is the event on?")
                event_phrase = listenForWord()

                #This ensures that if the person doesn't say on when they mention a specific date it still recognizes it
                t_event_phrase = tokenize(event_phrase)
                if t_event_phrase[0] in list(month_names.keys()):
                    event_phrase = "on " + event_phrase

    #This while loop handles getting the title of the event
    event_phrase = event_phrase_initial
    first = True
    while True:
        if "called" in event_phrase:
            cut_phrase = event_phrase[event_phrase.index("called")+6:]
            if "that" in cut_phrase:
                title = cut_phrase[0:cut_phrase.index("that")]
                title = title.strip()
            else:
                title = cut_phrase
                title = title.strip()
            break
        if "titled" in event_phrase:
            cut_phrase = event_phrase[event_phrase.index("titled")+6:]
            if "that" in cut_phrase:
                title = cut_phrase[:cut_phrase.index("that")]
                title = title.strip()
            else:
                title = cut_phrase
                title = title.strip()
            break
        if first == False:
            title = event_phrase
            break

        say("What is the event called?")
        event_phrase = listenForWord()
        first = False
        #Listen for new info

    print(title)
    print(start_time.isoformat())
    print(end_time.isoformat())
    print("Event Phrase: " + event_phrase)

    #The colors go from 1 to 11
    '''
    1 is lavendar
    2 is light green
    3 is pink
    4 is salmon
    5 is yellow
    6 is light orange
    7 is light blue
    8 is grey
    9 is dark blue
    10 is green
    11 is red
    '''
    #The numbers are all in a string format though

    concert_words = ["concert", "gig", "performance"]
    rehearsal_words = ["rehearsal", "practice"]
    social_words = ["dinner", "movie", "lunch", "hang out"]

    #Picking the color
    color_id = ''
    event_type_found = False
    for word in concert_words:
        if word in event_phrase:
            color_id = '2'
            event_type_found = True
            break
    for word in rehearsal_words:
        if word in event_phrase:
            color_id = '6'
            event_type_found = True
            break
    for word in social_words:
        if word in event_phrase:
            color_id = '7'
            event_type_found = True
            break
    if event_type_found == False:
        while True:
            color_id = str(random.randint(1,11))
            #Can't be any of the colors mentioned so far
            if color_id == '2' or color_id == '6' or color_id == '7':
                break

    print("Color ID: " + str(color_id))
    #Want to eventually figure out the time zone on it's own, but for now I manually inputed it
    event = {
        'summary': title,
        'colorId': color_id,
        'start':{
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/New_York'
        },
        'end': {
            "dateTime": end_time.isoformat(),
            'timeZone': 'America/New_York'
        },
    }

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    #This is basically the event class that you can do stuff to
    events = service.events()

    #This is how you add events
    events.insert(calendarId='primary', body=event).execute()
    say("An event has been added called " + str(title) + " on " + str(start_time.month) + " " + str(start_time.day) + " from " + str(start_time.hour) + " " + str(start_time.minute) + " to " + str(end_time.hour) + " " + str(end_time.minute))

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

commands = {"say": repeat, "weather": getWeather, "temp": getWeather, "remind": set_reminder, "timer": set_reminder, "alarm":set_alarm, "left": get_time_left, "time": get_time, "date": get_date, "calendar":set_event, "schedule":get_events, "exit": exit_program}

def say(phrase):
    engine.say(phrase)
    engine.runAndWait()

def listenForWord():
    with mic as source:
        #Just added this line, might slow it down a toooonnnnn
        recognizer.adjust_for_ambient_noise(source)

        print("Request")
        audio = recognizer.listen(source, phrase_time_limit=max_seconds)

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
        if keyPhrase1 in s:
            #This gets a string of everything said after the key phrase was said
            phraseSaid = s[s.find(keyPhrase1)+len(keyPhrase1):]
            key_phrase_said = True
            print("Key phrase said")
        elif keyPhrase2 in s:
            #This gets a string of everything said after the key phrase was said
            phraseSaid = s[s.find(keyPhrase2)+len(keyPhrase2):]
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
        print("Done with commands")
        key_phrase_said = False
        stop_listening = recognizer.listen_in_background(mic, callback)
    if len(timers) != 0:
        for i in range(len(timers)):
            #Timers contain the start and end dates
            if datetime.now() >= timers[i].get_time():
                stop_listening(wait_for_stop=True)

                #If the alarm is silenced set it to not be silent but don't go off
                #Otherwise just have the alarm ring
                if timers[i].is_silent() == False:
                    remind(i)
                else:
                    timers[i].set_silence(False)
                    del timers[i]

                stop_listening = recognizer.listen_in_background(mic, callback)
                break

    #If it switches to tomorrow add all of the new alarms
    if date.today() > tomorrow:
        #This code resets tomorrow
        today = date.today()
        tomorrow = today + timedelta(days=1)

        weekday = datetime.now().weekday()
        for alarm in alarms[weekday]:
            #This code alters the time of the alarm to make sure it is on the right day
            alarm_time = alarm.get_time()
            alarm_time.replace(day=today.day)
            alarm_time.replace(month=today.month)
            alarm_time.replace(year=today.year)
            alarm.set_time(alarm_time)

            timers.append(alarm)

#Stops the listening
stop_listening(wait_for_stop=True)
print("Doneeeeeeeeeee")
