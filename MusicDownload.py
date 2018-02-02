import pafy
from bs4 import BeautifulSoup
import urllib3
import urllib
import subprocess
import time
from pydub import AudioSegment

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

def get_song(phrase):
    t_phrase = tokenize(phrase)
    print(t_phrase)
    song = ""
    artist = ""
    if "play" in t_phrase and "by" in t_phrase:
        song = t_phrase[t_phrase.index("play") + 1:t_phrase.index("by")]
        artist = t_phrase[t_phrase.index("by") + 1:len(t_phrase)]
    elif "play" in t_phrase:
        song = t_phrase[t_phrase.index("play") + 1:len(t_phrase)]

    print(song)
    print(artist)
    search_url = "https://www.youtube.com/results?search_query="
    if artist == "":
        for word in song:
            search_url += word + "+"
    else:
        for word in song:
            search_url += word + "+"
        search_url += "by+"
        for word in artist:
            search_url += word + "+"

    search_url = search_url.strip("+")
    print(search_url)

    data = urllib.request.urlopen(search_url)
    youtube_searches = BeautifulSoup(data.read(),"html.parser")

    #The 4th one is the first search result
    search_results = youtube_searches.findAll('h3')

    #This gets the first link then creates a new url
    first_result = str(search_results[3])
    new_link = first_result[first_result.index("/watch?v="):first_result.index("/watch?v=") + 20]
    new_url = 'https://www.youtube.com' + new_link
    print(new_url)

    video = pafy.new(new_url)
    audio_streams = video.audiostreams
    for audio in audio_streams:
        print(audio)

    song = AudioSegment.from_file("C:\\Users\\DSleeps\\Documents\\GitHub\\Voice-Control\\Bleh.mp3", format="mp3")
    song.export("Songgg.wav", format="wav")
    #download = audio_streams[len(audio_streams) - 1].download(quiet=False)



get_song("play Bring me back")
