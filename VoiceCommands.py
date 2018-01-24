import numpy
import time
import speech_recognition as sr
import pyttsx3 as ps
from bs4 import BeautifulSoup
import urllib3

#The phrase you have to say to activate this
keyPhrase = "hey carl"
commandPhrase = "What do you need?"

recognizer = sr.Recognizer()
mic = sr.Microphone()
engine = ps.init()

#Set to true when the keyword is said
key_phrase_said = False

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

commands = {"say": repeat, "weather": getWeather, "temp": getWeather}

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

def listen_for_command():
    say(commandPhrase)
    command = listenForWord()
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
    if commandFound == False:
        say("Command not found")

def callback(recognizer, audio):
    global key_phrase_said

    print("Processing...")
    try:
        s = recognizer.recognize_google(audio)
        s = s.lower()
        print("You said: " + s)

        #Listens for the specific keyphrase
        if keyPhrase in s:
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
        listen_for_command()
        break

#Stops the listening
print("Done")
