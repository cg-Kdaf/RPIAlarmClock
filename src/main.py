#!/usr/bin/python3
# -*- coding:utf-8 -*-
import epd7in5_V2
from PIL import Image,ImageDraw,ImageFont
from datetime import datetime, timedelta
from math import ceil

from calendars import calendars, get_calendars_sorted, get_event_from_text, sort_events, get_calendar
from weather import get_weather_data, weather_intensity, icon_correspondance
from sound import speaker

# -- Datas

# Fonts
font_large = ImageFont.truetype('data/Font.ttc', 128)
font_medium = ImageFont.truetype('data/Teko/Teko-Light.ttf', 32)
font_weather = ImageFont.truetype('data/weather_font.ttf', 40)
font_time_l = ImageFont.truetype('data/Orbitron/static/Orbitron-Regular.ttf', 64)
font_time_s = ImageFont.truetype('data/Orbitron/static/Orbitron-SemiBold.ttf', 24)
font_time_xs = ImageFont.truetype('data/Teko/Teko-Medium.ttf', 26)
font_time_xs_bold = ImageFont.truetype('data/Teko/Teko-Medium.ttf', 24)

# Datas --

def cut_text_to_length(image, text_, font_, length, min_char_length):
    char_length_end = min_char_length
    actual_length = 0
    
    while actual_length < length:
        if char_length_end > len(text_):
            break
        text_w, text_h = image.textsize(text_[:char_length_end], font=font_)
        actual_length = text_w
        char_length_end += 1
    return text_[:char_length_end-1]

def draw_text_angle(image, image_g, position_, text_, font_, fill_, angle_):
    """(image, position_, text_, font_, fill_, angle_)"""
    text_w, text_h = image.textsize(text_, font=font_)
    txt=Image.new('1', (text_w,text_h), 255)
    d = ImageDraw.Draw(txt)
    d.text((0,0), text_,  font=font_, fill=fill_)
    txt_=txt.rotate(angle_,  expand=True)

    image_g.paste(txt_, box = position_)
    #image_g.paste(txt, box = position_)


def draw_time(image,Image_global):
    layout_w = (0,330)
    layout_h = (0,60)

    image.rectangle((layout_w[0], layout_h[1], layout_w[1], layout_h[1]+4), fill = 0) # Separator bottom
    image.rectangle((layout_w[1], layout_h[0], layout_w[1]+2, layout_h[1]+4), fill = 0) # Separator right

    now=datetime.now()+timedelta(minutes = 1)
    date_text = now.strftime("%A\n%d %b") # Date as Friday\n01 Jan
    text1_w, text1_h = image.textsize(date_text, font=font_time_s)
    image.text((layout_w[1]-text1_w, layout_h[0]), date_text, font = font_time_s, fill = 0) # Draw date
    time_text = now.strftime("%k:%M") # Time as 14:03 or 3:50
    text2_w, text2_h = image.textsize(time_text, font=font_time_l)
    image.text(((layout_w[1]-text1_w-text2_w)/2, layout_h[0]-15), time_text, font = font_time_l, fill = 0) # Draw time

def draw_weather(image,Image_global):
    now=datetime.now()
    layout_w = (330,800)
    layout_h = (0,60)
    
    image.rectangle((layout_w[0], layout_h[1], layout_w[1], layout_h[1]+4), fill = 0) # Separator bottom
    
    average_main_props = ("feels_like","temp","temp_min","temp_max")
    start_day = datetime(2000,1,1,5)
    end_day = datetime(2000,1,1,22)
    weather_data = {}
    for index, data in enumerate(get_weather_data()):
        time_datetime = datetime.strptime(data["dt_txt"],'%Y-%m-%d %H:%M:%S')
        date_str = str(time_datetime.date())
        if time_datetime.time() > end_day.time() or time_datetime.time() < start_day.time():
            continue
        if date_str not in weather_data.keys():
            weather_data[date_str] = data
        else:
            weather_data[date_str]["main"]["temp_min"] = min(data["main"]["temp_min"], weather_data[date_str]["main"]["temp_min"])
            weather_data[date_str]["main"]["temp_max"] = max(data["main"]["temp_max"], weather_data[date_str]["main"]["temp_max"])
    for index_day, day in enumerate(weather_data):
        pos_x = layout_w[0]+80*index_day
        date = datetime.strptime(day,'%Y-%m-%d')
        date_text = ("Today" if now.date() == date.date() else cut_text_to_length(image, date.strftime('%A'), font_time_xs_bold, 55, 5))
        draw_text_angle(image, Image_global, (pos_x+4,0), date_text, font_time_xs_bold, 0, 90)
        for index_part, prop in enumerate(["temp_min","temp_max"]):
            pos_y = index_part*30
            image.text((pos_x + 30, pos_y), f'{round(weather_data[day]["main"][prop])}°', font = font_time_xs, fill = 0)

def draw_calendar(image,Image_global):
    layout_w = (0,800)
    layout_h = (62,480)
    event_height = 30
    events_number = ceil((layout_h[1] - layout_h[0]) / event_height)
    events = get_calendars_sorted(calendars[:3])[:events_number]
    drawn_dates = []
    for index, event in enumerate(events):
        pos_y = layout_h[0] + event_height * index + len(drawn_dates) * 3
        time_start = event["DTSTART"]
        if str(time_start.date()) not in drawn_dates:
            drawn_dates.append(str(time_start.date()))
            pos_y = layout_h[0] + event_height * index + len(drawn_dates) * 3
            image.text((layout_w[0]+4, pos_y), time_start.strftime("%a"), font = font_time_xs, fill = 0) # Draw the date
            image.rectangle((layout_w[0], pos_y+15, layout_w[0]+1, pos_y+event_height), fill = 0) # draw the left bar small size
            if len(drawn_dates) != 1 : # Draw horizontal line only if not the first day
                image.rectangle((layout_w[0], pos_y - 2, layout_w[0] + 160, pos_y - 1), fill = 0) # draw the horizontal bar
        else:
            image.text((layout_w[0]+4, pos_y), time_start.strftime("%H:%M"), font = font_time_xs, fill = 0) # draw the start time
            image.rectangle((layout_w[0], pos_y, layout_w[0]+1, pos_y+event_height), fill = 0) # draw the left bar entire size
        image.text((layout_w[0]+60, pos_y), cut_text_to_length(draw,event["SUMMARY"], font_time_xs, 110, 6), font = font_time_xs, fill = 0)

def compare_time_to_alarm(alarms_passed, speaker):
    alarm_comming = sort_events(get_event_from_text(get_calendar(calendars[3]),True,True))
    if len(alarm_comming) > 0:
        alarm_comming = alarm_comming[0]
    
    if alarm_comming == []:
        return
    if alarm_comming["STATUS"] == 1 and alarm_comming["SUMMARY"] not in alarms_passed:
        speaker.ring()
        print("RINGING !!")
        alarms_passed.append(alarm_comming["SUMMARY"])
    


try:
    from time import time as time_time, sleep as time_sleep
    starttime = time_time()
    
    
    print("Program starts")
    print("Initialisation...")
    refresh_time = 180 # Refresh every x seconds
    print(f"Will refresh every {refresh_time} seconds")
    speaker = speaker()
    #Init display
    epd = epd7in5_V2.EPD()
    alarms_passed = []
    while True:
        print("Refresh", datetime.now())
        compare_time_to_alarm(alarms_passed, speaker)
        
        epd.init()
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)

        print("...\nComputing image")
        draw_time(draw,Himage)
        draw_weather(draw,Himage)
        draw_calendar(draw,Himage)

        print("...\nDrawing image")
        epd.display(epd.getbuffer(Himage))
        print("...\nSleeping")
        epd.sleep()
        
        
        time_to_sleep = refresh_time - ((time_time() - starttime) % refresh_time)
        time_sleep(time_to_sleep)

finally:
    print("Program ended.")
    epd.Dev_exit()
    speaker.clean_gpio()
