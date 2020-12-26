#!/usr/bin/python
import json
import urllib.request
import datetime

city1_id="2996881"
APPID="7ba1b7bb6563f08710a3a8138767bf32"
unit="metric"
openweathermap="http://api.openweathermap.org/data/2.5/forecast"
month=("Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec")

id_ranges=((200,233),(300,322),(500,532),(600,623),(701,782),(801,805))
# Correspond to thunderstorm, drizzle, rain, snow, atmosphere, clouds
icon_correspondance = {
    "01": 97,
    "02": 99,
    "03": 100,
    "04": 101,
    "09": 104,
    "10": 103,
    "11": 102,
    "13": 106,
    "50": 98
}
# Icon correspondance between openweathermap (https://openweathermap.org/weather-conditions)
# and the ascii caracter of the font (https://www.dafont.com/weather.font)


def get_weather_data():
    # Construction de l'url OpenWeatherMap
    url_openweathermap  = openweathermap + '?id=' + city1_id + '&units=' + unit + '&APPID=' + APPID

    try:
        # Récupération des prévisions météo et décodage JSON
        webURL = urllib.request.urlopen(url_openweathermap)
        data = webURL.read()
        encoding = webURL.info().get_content_charset('utf-8')
        infos=json.loads(data.decode(encoding))
    except:
        print("error searching weather data from : "+url_openweathermap);
        exit(1)

    
    weather_data=[]
    for item in infos["list"]:
        date_1 = str(item["dt_txt"]).split(" ")[0].split("-")
        date_2 = str(item["dt_txt"]).split(" ")[1].split(":")
        if int(date_1[2]) == datetime.datetime.now().day:
            date = "Today"
        elif int(date_1[2]) == (datetime.datetime.now()+datetime.timedelta(days=1)).day:
            date = "Tomor"
        else:
            date = f"{int(date_1[2]):02d}{month[int(date_1[1])-1]}"
        date += f";{int(date_2[0]):02d}h"
        index = item["weather"][0]["id"]
        percentage = 0
        for id_range in id_ranges:
            if index in range(id_range[0],id_range[1]):
                percentage = (index-id_range[0])/(id_range[1]-id_range[0])*100
                continue
        main = item["weather"][0]["main"]
        main += f" {int(percentage):2d}%"
        temperature = item["main"]["temp"]
        
        icon = icon_correspondance[str(item["weather"][0]["icon"][0:2])]
        #if item["weather"][0]["icon"][2] == "n":
            #icon += 10
        daynight = item["weather"][0]["icon"][2]
        
        # humidity = item["main"]["humidity"]
        # pressure = item["main"]["pressure"]
        weather_data.append((date,main,temperature,icon,daynight))
    return weather_data
