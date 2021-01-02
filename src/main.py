#!/usr/bin/python3
# -*- coding:utf-8 -*-
import epd7in5_V2
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime

from weather import get_weather_data, weather_intensity, icon_correspondance

# -- Datas

# Fonts
font_large = ImageFont.truetype('data/Font.ttc', 128)
font_medium = ImageFont.truetype('data/Teko/Teko-Light.ttf', 32)
font_weather = ImageFont.truetype('data/weather_font.ttf', 40)
font_time_l = ImageFont.truetype('data/Orbitron/static/Orbitron-Regular.ttf', 64)
font_time_s = ImageFont.truetype('data/Orbitron/static/Orbitron-SemiBold.ttf', 24)
font_time_xs = ImageFont.truetype('data/Teko/Teko-Light.ttf', 26)
font_time_xs_bold = ImageFont.truetype('data/Teko/Teko-Medium.ttf', 24)

# Datas --

def draw_text_angle(image, image_g, position_, text_, font_, fill_, angle_):
    """(image, position_, text_, font_, fill_, angle_)"""
    text_w, text_h = image.textsize(text_, font=font_)
    txt=Image.new('1', (text_w,text_h), 255)
    d = ImageDraw.Draw(txt)
    d.text((0,0), text_,  font=font_, fill=fill_)
    txt_=txt.rotate(angle_,  expand=True)

    image_g.paste(txt_, box = position_)
    #image_g.paste(txt, box = position_)


def draw_time(image):
    layout_w = (0,330)
    layout_h = (0,60)
    time_w = (layout_w[0],layout_w[0]+225)

    image.rectangle((layout_w[0], layout_h[1], layout_w[1], layout_h[1]+4), fill = 0) # Separator bottom
    image.rectangle((layout_w[1], layout_h[0], layout_w[1]+2, layout_h[1]+4), fill = 0) # Separator right

    now=datetime.now()
    time_text = now.strftime("%k:%M") # Time as 10:03 or 3:50
    text_w, text_h = image.textsize(time_text, font=font_time_l)
    image.text((time_w[0]+(time_w[1]-text_w)/2, layout_h[0]-15), time_text, font = font_time_l, fill = 0)
    date_text = now.strftime("%A\n%d %b") # Date as Friday\n01 Jan
    text_w, text_h = image.textsize(date_text, font=font_time_s)
    image.text((time_w[1]+(layout_w[1]-time_w[1]-text_w)/2, layout_h[0]), date_text, font = font_time_s, fill = 0)

def draw_weather(image,Image_global): # TODO Draw the min/max temp of the day instead of medium of midday
    now=datetime.now()
    layout_w = (330,800)
    layout_h = (0,60)
    
    image.rectangle((layout_w[0], layout_h[1], layout_w[1], layout_h[1]+4), fill = 0) # Separator bottom
    
    average_main_props = ("feels_like","temp","temp_min","temp_max")
    start_day = datetime(2000,1,1,7)
    mid_day = datetime(2000,1,1,12,30)
    end_day = datetime(2000,1,1,20)
    weather_data = {}
    for index, data in enumerate(get_weather_data()):
        time_datetime = datetime.strptime(data["dt_txt"],'%Y-%m-%d %H:%M:%S')
        date_str = str(time_datetime.date())
        suffix_str = ("Morning" if time_datetime.time() < mid_day.time() else "Afternoon")
        if time_datetime.time() > end_day.time() or time_datetime.time() < start_day.time():
            continue
        if date_str not in weather_data.keys():
            weather_data[date_str] = {}
        if suffix_str not in weather_data[date_str].keys():
            weather_data[date_str][suffix_str] = data
        else:
            for prop in average_main_props:
                weather_data[date_str][suffix_str]["main"][prop] += data["main"][prop]
                weather_data[date_str][suffix_str]["main"][prop] *= 0.5
    for index_day, day in enumerate(weather_data):
        pos_x = layout_w[0]+85*index_day
        parts = list(weather_data[day].keys())
        date = datetime.strptime(day,'%Y-%m-%d')
        date_text = ("Today" if now.date() == date.date() else date.strftime('%A')[:6])
        draw_text_angle(image, Image_global, (pos_x+4,0), date_text, font_time_xs_bold, 0, 90)
        for index_part, part in enumerate(parts):
            pos_y = (15 if len(parts) == 1 else index_part*30)
            image.text((pos_x + 30, pos_y), f'{weather_data[day][part]["main"]["temp"]:4.1f}°C', font = font_time_xs, fill = 0)

# Init display
epd = epd7in5_V2.EPD()
epd.init()
Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
draw = ImageDraw.Draw(Himage)

print("...\nComputing image")
draw_time(draw)
draw_weather(draw,Himage)


print("...\nDrawing image")
epd.display(epd.getbuffer(Himage))
print("...\nSleeping")
epd.sleep()
epd.Dev_exit()
