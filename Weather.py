from bs4 import BeautifulSoup
import urllib3

def getWeather(phrase):
    weather_url = "https://weather.com/weather/tenday/l/USMA0046:1:US"
    http_pool = urllib3.connection_from_url(weather_url)
    html = http_pool.urlopen('Get',weather_url)
    html = html.data

    weather_site = BeautifulSoup(html, "html.parser")
    tableRows = weather_site.findAll('tr')

    day = 1

    if 'today' in phrase:
        day = 1
    elif 'tomorrow' in phrase:
        day = 2

    infoList = tableRows[day].findAll('span')

    day_of_week = infoList[0].contents[0]
    day = infoList[1].contents[0]
    weather = infoList[2].contents[0]
    high = infoList[3].contents[0]
    low = infoList[5].contents[0]
    precipitation_chance = infoList[8].contents[0]

    if 'temp' in phrase:
        print("The low is " + str(low) + " and the high is " + str(high))
        return None
    else:
        td = tableRows[day].findAll('td')
        text = ""
        s_td = str(td)

        for i in range(s_td.find("title")+7,len(s_td)):
            if s_td[i] == "\"":
                break
            else:
                text = text + s_td[i]

        print(text)

getWeather("What is the temperature like today")
