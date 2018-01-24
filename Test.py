import numpy
import time
import speech_recognition as sr

#The phrase you have to say to activate this
keyPhrase = "hey carl"

r = sr.Recognizer()
mic = sr.Microphone()

#Set to true when the keyword is said
listeningForCommand = False

#All of the commands
def say(phrase):
    print(phrase)

commands = {"say": say}

def listenForWord():

    with mic as source:
        print("Request a command")
        audio = recognizer.listen(source)

    #Processes the audio
    try:
        words = recognizer.recognize_google(audio)
        return words
    except sr.UnknownValueError:
        print("Got nothing")
        return ""
    except sr.RequestError:
        print("Didn't work")
        return ""

def executeCommand(command):
    commandFound = False
    for commandKey in list(commands.keys()):
        #If the key is somewhere in the command extract the command key and just leave the information
        if commandKey in command:
            print("Command: " + commandKey)
            #This clears the command word and only leaves what is said after
            words = command[len(commandKey):]
            #Gets rid of all of the extra spaces before and after the word
            words = words.strip()
            #Calls whatever command is in the dictionary of commands
            commands[commandKey](words)
            commandFound = True
    if commandFound == False:
        print("Command not found")

def callback(recognizer, audio):
    global listeningForCommand

    print("Processing...")
    try:
        s = recognizer.recognize_google(audio)
        s = s.lower()
        print("You said: " + s)

        #Listens for the specific keyphrase
        if keyPhrase in s:
            listeningForCommand = True
            print("Say a command")
        elif listeningForCommand == True:
            executeCommand(s)

    except sr.UnknownValueError:
        print("Got nothing")
    except sr.RequestError:
        print("Didn't work")

with mic as source:
    r.adjust_for_ambient_noise(source)

#Starts listening but creates a function that can stop the listening
print("Starting...")
stop_listening = r.listen_in_background(mic, callback)
print("Ready")

time.sleep(10)

#Stops the listening
stop_listening(wait_for_stop=True)
print("Done")
