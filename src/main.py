#!/usr/bin/python3
# -*- coding:utf-8 -*-
import epd7in5_V2
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime

from weather import get_weather_data

# -- Datas

# Fonts
font_large = ImageFont.truetype('data/Font.ttc', 128)
font_medium = ImageFont.truetype('data/Teko/Teko-Light.ttf', 32)
font_weather = ImageFont.truetype('data/weather_font.ttf', 40)
font_time_l = ImageFont.truetype('data/Orbitron/static/Orbitron-Regular.ttf', 64)
font_time_s = ImageFont.truetype('data/Orbitron/static/Orbitron-SemiBold.ttf', 24)

# Datas --

def draw_time(image):
    layout_w = (0,330)
    layout_h = (0,60)
    time_w = (layout_w[0],layout_w[0]+225)

    image.rectangle((layout_w[0], layout_h[1], layout_w[1], layout_h[1]+4), fill = 0) # Separator bottom
    image.rectangle((layout_w[1], layout_h[0], layout_w[1]+4, epd.height), fill = 0) # Separator right

    now=datetime.now()
    time_text = now.strftime("%k:%M") # Time as 10:03 or 3:50
    text_w, text_h = image.textsize(time_text, font=font_time_l)
    image.text((time_w[0]+(time_w[1]-text_w)/2, layout_h[0]-15), time_text, font = font_time_l, fill = 0)
    date_text = now.strftime("%A\n%d %b") # Date as Friday\n01 Jan
    text_w, text_h = image.textsize(date_text, font=font_time_s)
    image.text((time_w[1]+(layout_w[1]-time_w[1]-text_w)/2, layout_h[0]), date_text, font = font_time_s, fill = 0)

def draw_weather(image):
    ranges = ((0,7),(8,13),(14,19))
    
    image.text((340,0), "Time", font = font_medium , fill = 0)
    image.text((500,0), "Temp", font = font_medium , fill = 0)
    image.text((620,0), "Trending", font = font_medium , fill = 0)
    image.rectangle((324, 31, 800, 33), fill = 0)
    days = {}
    for data in get_weather_data():
        day_part_suffix = ""
        for index, day_part in enumerate(ranges):
            if data[5] in day_part:
                day_part_suffix = str(index)
                break
        day_part_name = data[0] + day_part_suffix
        if day_part_name not in days.keys():
            days[day_part_name] = []
        days[day_part_name].append([data[1],data[2],data[3]])
    for index, data in enumerate(get_weather_data()):
        image.text((340,(index+1)*32), str(data[0]), font = font_medium, fill = 0) # Time
        image.text((500,(index+1)*32), f"{data[2]:4.1f}°C", font = font_medium , fill = 0) # Temp
        image.text((600,(index+1)*32), chr(data[3]), font = font_weather, fill = 0) # Icon
        image.text((620,(index+1)*32), str(data[1]), font = font_medium, fill = 0) # Trending


# Init display
epd = epd7in5_V2.EPD()
epd.init()
Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
draw = ImageDraw.Draw(Himage)

print("...\nComputing image")
draw_time(draw)
draw_weather(draw)


print("...\nDrawing image")
epd.display(epd.getbuffer(Himage))
print("...\nSleeping")
epd.sleep()
epd.Dev_exit()
