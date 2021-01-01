#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

import logging
import epd7in5_V2
import time
from datetime import datetime
from PIL import Image,ImageDraw,ImageFont
import traceback

from weather import get_weather_data

logging.basicConfig(level=logging.DEBUG)

try:
    epd = epd7in5_V2.EPD()
    
    print("...\nCleaning display ( ",epd.width,"by",epd.height,"px )")
    epd.init()
    epd.Clear()

    font_large = ImageFont.truetype('data/Font.ttc', 128)
    font_medium = ImageFont.truetype('data/Font.ttc', 32)
    font_weather = ImageFont.truetype('data/weather_font.ttf', 40)

    # Drawing on the Horizontal image
    print("...\nDisplaying time")
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    draw.rectangle((0, 128, 324, 132), fill = 0)
    draw.rectangle((324, 0, 328, 480), fill = 0)

    date=datetime.now()
    time_text = f"{date.hour:02d}:{date.minute:02d}"
    draw.text((0, 0), time_text, font = font_large, fill = 0)

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
        
    epd.display(epd.getbuffer(Himage))

    print("...\nSleeping")
    epd.sleep()
    epd.Dev_exit()

except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit()
    exit()
