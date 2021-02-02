#!/usr/bin/python3
import epd7in5_V2
import logging
from PIL import Image as Image_class, ImageDraw, ImageFont, ImageOps
from datetime import datetime, timedelta
from math import ceil

from calendars import get_calendar_sorted
from weather import get_weather_data


def cut_text_to_length(Image_Draw, text_, font_, length, min_char_length):
    char_length_end = min_char_length
    actual_length = 0

    while actual_length < length:
        if char_length_end > len(text_):
            break
        text_w, text_h = Image_Draw.textsize(text_[:char_length_end], font=font_)
        actual_length = text_w
        char_length_end += 1
    return text_[:char_length_end-1]


def draw_text_angle(image, image_g, position_, text_, font_, angle_, fill_=0):
    """(image, position_, text_, font_, fill_, angle_)"""
    text_w, text_h = image.textsize(text_, font=font_)
    txt = Image_class.new('1', (text_w, text_h), 255)
    d = ImageDraw.Draw(txt)
    d.text((0,0), text_,  font=font_, fill=fill_)
    txt_ = txt.rotate(angle_,  expand=True)

    image_g.paste(txt_, box=position_)


class Display():
    def __init__(self):
        logging.info("Creating EPD (ElectronicPaperDisplay) object")
        self.font_large = ImageFont.truetype('data/Font.ttc', 128)
        self.font_medium = ImageFont.truetype('data/Teko/Teko-Light.ttf', 32)
        self.font_weather = ImageFont.truetype('data/weather_font.ttf', 40)
        self.font_time_l = ImageFont.truetype('data/Orbitron/static/Orbitron-Regular.ttf', 64)
        self.font_time_s = ImageFont.truetype('data/Orbitron/static/Orbitron-SemiBold.ttf', 24)
        self.font_time_xs = ImageFont.truetype('data/Teko/Teko-Medium.ttf', 26)
        self.font_time_xs_bold = ImageFont.truetype('data/Teko/Teko-Medium.ttf', 24)
        self.ring_icon = Image_class.open('data/bell.bmp')
        self.image_bike = Image_class.open('data/image_bike2.bmp')

        self.invert = False

        self.epd = epd7in5_V2.EPD()

    def draw_time(self, Image_Draw, Image_global):
        layout_w = (0, 330)
        layout_h = (0, 60)

        # Separator bottom
        Image_Draw.rectangle((layout_w[0], layout_h[1], layout_w[1], layout_h[1]+4), fill = 0)
        # Separator right
        Image_Draw.rectangle((layout_w[1], layout_h[0], layout_w[1]+2, layout_h[1]+4), fill = 0)

        now = datetime.now()+timedelta(minutes=1)
        date_text = now.strftime("%A\n%d %b")  # Date as Friday\n01 Jan
        text1_w, text1_h = Image_Draw.textsize(date_text, font=self.font_time_s)
        Image_Draw.text((layout_w[1]-text1_w, layout_h[0]), date_text, font=self.font_time_s, fill=0) # Draw date
        time_text = now.strftime("%k:%M")  # Time as 14:03 or 3:50
        text2_w, text2_h = Image_Draw.textsize(time_text, font=self.font_time_l)
        Image_Draw.text(((layout_w[1]-text1_w-text2_w)/2, layout_h[0]-15), time_text, font=self.font_time_l, fill=0) # Draw time
        # Draw a widget for the Alarm
        activated = open("/home/pi/AlarmClockProject/AlarmClock/cache/alarm_status", "r").read()
        if "1" in activated:
            Image_global.paste(self.ring_icon, (layout_w[1] - 30, layout_h[1] - 30))

    def draw_weather(self, Image_Draw, Image_global):
        now = datetime.now()
        layout_w = (330, 800)
        layout_h = (0, 60)

        Image_Draw.rectangle((layout_w[0], layout_h[1], layout_w[1], layout_h[1]+4), fill = 0) # Separator bottom

        start_day = datetime(2000, 1, 1, 5)
        end_day = datetime(2000, 1, 1, 22)
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
            date_text = ("Today" if now.date() == date.date() else cut_text_to_length(Image_Draw, date.strftime('%A'), self.font_time_xs_bold, 55, 5))
            draw_text_angle(Image_Draw, Image_global, (pos_x+4,0), date_text, self.font_time_xs_bold, 90)
            for index_part, prop in enumerate(["temp_min","temp_max"]):
                pos_y = index_part*30
                Image_Draw.text((pos_x + 30, pos_y), f'{round(weather_data[day]["main"][prop])}°', font = self.font_time_xs, fill = 0)

    def draw_calendar(self, Image_Draw, Image_global):
        layout_w = (0,800)
        layout_h = (62,480)
        event_height = 30
        events_number = ceil((layout_h[1] - layout_h[0]) / event_height)
        events = get_calendar_sorted(range(3))[:events_number]
        drawn_dates = []
        for index, event in enumerate(events):
            pos_y = layout_h[0] + event_height * index + len(drawn_dates) * 3
            time_start = event["DTSTART"]
            if str(time_start.date()) not in drawn_dates:
                drawn_dates.append(str(time_start.date()))
                pos_y = layout_h[0] + event_height * index + len(drawn_dates) * 3
                Image_Draw.text((layout_w[0]+4, pos_y), time_start.strftime("%a"), font = self.font_time_xs, fill = 0) # Draw the date
                Image_Draw.rectangle((layout_w[0], pos_y+15, layout_w[0]+1, pos_y+event_height), fill = 0) # draw the left bar small size
                if len(drawn_dates) != 1 : # Draw horizontal line only if not the first day
                    Image_Draw.rectangle((layout_w[0], pos_y - 2, layout_w[0] + 160, pos_y - 1), fill = 0) # draw the horizontal bar
            else:
                Image_Draw.text((layout_w[0]+4, pos_y), time_start.strftime("%H:%M"), font = self.font_time_xs, fill = 0) # draw the start time
                Image_Draw.rectangle((layout_w[0], pos_y, layout_w[0]+1, pos_y+event_height), fill = 0) # draw the left bar entire size
            Image_Draw.text((layout_w[0]+60, pos_y), cut_text_to_length(Image_Draw,event["SUMMARY"], self.font_time_xs, 110, 6), font = self.font_time_xs, fill = 0)

    def draw_image(self, Image_Draw, Image_global):
        image_width, image_height = self.image_bike.size
        Image_global.paste(self.image_bike, (800-image_width, 480-image_height))

    def refresh(self):
        logging.info("Initialising display")
        self.epd.init()
        logging.info("Computing image")
        Image = Image_class.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
        Draw = ImageDraw.Draw(Image)
        self.draw_weather(Draw, Image)
        self.draw_time(Draw, Image)
        self.draw_calendar(Draw, Image)
        # self.draw_image(Draw, Image)
        if self.invert:
            Image = ImageOps.mirror(Image)  # Mirror image in horizontal axis
            Image = Image.convert('L')  # Convert image to something invertable
            Image = ImageOps.invert(Image)  # Invert BW image
            Image = Image.convert('1')  # convert back to BlackWhite
        logging.info("Sending image to display")
        self.epd.display(self.epd.getbuffer(Image))
        logging.info("Sleeping")
        self.epd.sleep()

    def exit(self):
        self.epd.Dev_exit()
        logging.info("Releasing EPD")
