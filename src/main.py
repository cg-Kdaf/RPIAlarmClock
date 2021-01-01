#!/usr/bin/python3
# -*- coding:utf-8 -*-
import epd7in5_V2
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime

from weather import get_weather_data

# Init display
epd = epd7in5_V2.EPD()
epd.init()
Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
draw = ImageDraw.Draw(Himage)

# Datas
font_large = ImageFont.truetype('data/Font.ttc', 128)
font_medium = ImageFont.truetype('data/Teko/Teko-Light.ttf', 32)
font_weather = ImageFont.truetype('data/weather_font.ttf', 40)
font_time_l = ImageFont.truetype('data/Orbitron/static/Orbitron-Regular.ttf', 64)
font_time_s = ImageFont.truetype('data/Orbitron/static/Orbitron-SemiBold.ttf', 24)

print("...\nComputing image")
# Draw time
layout_w = (0,324)
layout_h = (0,60)
time_w = (layout_w[0],layout_w[0]+190)

draw.rectangle((layout_w[0], layout_h[1], layout_w[1], layout_h[1]+4), fill = 0)
draw.rectangle((layout_w[1], layout_h[0], layout_w[1]+4, epd.height), fill = 0)

now=datetime.now()
time_text = now.strftime("%k:%M") # Time as 10:03 or 3:50
text_w, text_h = draw.textsize(time_text, font=font_time_l)
draw.text((time_w[0]+(time_w[1]-text_w)/2, layout_h[0]-15), time_text, font = font_time_l, fill = 0)
date_text = now.strftime("%a %d\n%b %Y") # Date as Fri 01\nJan 2021
draw.text((time_w[1], layout_h[0]), date_text, font = font_time_s, fill = 0)

# Draw weather
draw.text((340,0), "Time", font = font_medium , fill = 0)
draw.text((500,0), "Temp", font = font_medium , fill = 0)
draw.text((620,0), "Trending", font = font_medium , fill = 0)
draw.rectangle((324, 31, 800, 33), fill = 0)
for index, data in enumerate(get_weather_data()):
    draw.text((340,(index+1)*32), str(data[0]), font = font_medium, fill = 0) # Time
    draw.text((500,(index+1)*32), f"{data[2]:4.1f}°C", font = font_medium , fill = 0) # Temp
    draw.text((600,(index+1)*32), chr(data[3]), font = font_weather, fill = 0) # Icon
    draw.text((620,(index+1)*32), str(data[1]), font = font_medium, fill = 0) # Trending
    #if data[4] == "n":
        # draw.rectangle
        # TODO draw rectangle where the 

print("...\nDrawing image")
epd.display(epd.getbuffer(Himage))
print("...\nSleeping")
epd.sleep()
epd.Dev_exit()
