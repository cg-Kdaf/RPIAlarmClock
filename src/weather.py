#!/usr/bin/python3
import json

city1_id = "2996881"
APPID = "7ba1b7bb6563f08710a3a8138767bf32"
unit = "metric"
openweathermap = "http://api.openweathermap.org/data/2.5/forecast"
month = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

id_ranges = ((200, 233), (300, 322), (500, 532), (600, 623), (701, 782), (801, 805))
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

# def weather_intensity(weather_index):
#     for id_range in id_ranges:
#         if index in range(id_range[0],id_range[1]):
#             return (index-id_range[0])/(id_range[1]-id_range[0])*100

# Icon correspondance between openweathermap (https://openweathermap.org/weather-conditions)
# and the ascii caracter of the font (https://www.dafont.com/weather.font)


def get_weather_data():
    infos = json.loads(open("/home/pi/AlarmClockProject/AlarmClock/cache/weathers/weather0.json", "r").read())
    return infos["list"]
