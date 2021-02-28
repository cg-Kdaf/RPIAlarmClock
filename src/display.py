#!/usr/bin/python3
import epd7in5_V2
import logging
import json
from PIL import Image as Image_class, ImageDraw, ImageFont, ImageOps
from datetime import datetime, timedelta
from calendars import get_calendar_sorted
from weather import get_weather_data

# logging.basicConfig(level=logging.DEBUG)


def cut_text_to_length(Image_Draw, text_, font_, length, min_char_length):
    char_length_end = min_char_length
    actual_length = 0

    while actual_length < length:
        char_length_end += 1
        if char_length_end > len(text_):
            break
        text_w, text_h = Image_Draw.textsize(text_[:char_length_end], font=font_)
        actual_length = text_w
    return text_[:char_length_end-1]


def draw_text_angle(image, image_g, position_, text_, font_, angle_, fill_=0):
    """(image, position_, text_, font_, fill_, angle_)"""
    text_w, text_h = image.textsize(text_, font=font_)
    txt = Image_class.new('1', (text_w, text_h), 255)
    d = ImageDraw.Draw(txt)
    d.text((0,0), text_,  font=font_, fill=fill_)
    txt_ = txt.rotate(angle_,  expand=True)

    image_g.paste(txt_, box=position_)


def round_corner(radius, fill):
    """Draw a round corner"""
    corner = Image_class.new('1', (radius, radius), 255-fill)
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner


def round_rect(size, radius, fill, corners="1111"):
    """Draw a rounded rectangle"""
    width, height = size
    rectangle = Image_class.new('1', size, fill)
    corner = round_corner(radius, fill)
    if corners[0] == '1':
        rectangle.paste(corner, (0, 0))
    if corners[3] == '1':
        rectangle.paste(corner.rotate(90), (0, height - radius))  # Rotate the corner and paste it
    if corners[2] == '1':
        rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    if corners[1] == '1':
        rectangle.paste(corner.rotate(270), (width - radius, 0))
    return rectangle


def display_error(Image_Draw, xy, error_str):
    font_ = ImageFont.truetype('data/Teko/Teko-Light.ttf', 32)
    Image_Draw.text(xy, error_str, font=font_, fill=0)


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
        self.homework_icon = Image_class.open('data/homework.bmp')
        self.image_bike = Image_class.open('data/image_bike2.bmp')
        self.happening_events = []

        self.invert = False

        self.epd = epd7in5_V2.EPD()

    def draw_time(self, Image_Draw, Image_global):
        layout_w = (0, 330)
        layout_h = (0, 60)

        # Separator bottom
        Image_Draw.line((layout_w[0], layout_h[1], layout_w[1], layout_h[1]), width=4, fill=0)
        # Separator right
        Image_Draw.line((layout_w[1], layout_h[0], layout_w[1], layout_h[1]), width=2, fill=0)

        now = datetime.now()+timedelta(minutes=1)
        date_text = now.strftime("%A\n%d %b")  # Date as Friday\n01 Jan
        text1_w, text1_h = Image_Draw.textsize(date_text, font=self.font_time_s)
        Image_Draw.text((layout_w[1]-text1_w, layout_h[0]), date_text, font=self.font_time_s, fill=0)  # Draw date
        time_text = now.strftime("%k:%M")  # Time as 14:03 or 3:50
        text2_w, text2_h = Image_Draw.textsize(time_text, font=self.font_time_l)
        Image_Draw.text(((layout_w[1]-text1_w-text2_w)/2, layout_h[0]-15), time_text, font=self.font_time_l, fill=0)  # Draw time
        # Draw a widget for the Alarm
        activated = open("/home/pi/AlarmClockProject/AlarmClock/cache/alarm_status", "r").read()
        if "1" in activated:
            Image_global.paste(self.ring_icon, (layout_w[1] - 30, layout_h[1] - 30))

    def draw_weather(self, Image_Draw, Image_global):
        now = datetime.now()
        layout_w = (330, 800)
        layout_h = (0, 60)

        Image_Draw.line((layout_w[0], layout_h[1], layout_w[1], layout_h[1]), width=4, fill=0)  # Separator bottom

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
        self.happening_events = []
        layout_w = (0, 180)
        layout_h = (62, 480)
        # Image_Draw.line((layout_w[1], layout_h[0], layout_w[1], layout_h[1]), width=2, fill=0)
        event_h = 26
        event_h_half = int(event_h/2)
        date_w = 58
        sum_char = 18
        events_number = int((layout_h[1] - layout_h[0]) / event_h)+1
        events = get_calendar_sorted(range(2), get_ed=True)[:events_number]
        events_sorted = {}
        for event in events:
            if event["STATUS"] != 0:
                if "Now" not in events_sorted.keys():
                    events_sorted["Now"] = []
                events_sorted["Now"].append(event)
                self.happening_events.append(event)
            elif event["DTSTART"].date() == datetime.now().date():
                if "Today" not in events_sorted.keys():
                    events_sorted["Today"] = []
                events_sorted["Today"].append(event)
            else:
                if event["DTSTART"].date() not in events_sorted.keys():
                    events_sorted[event["DTSTART"].date()] = []
                events_sorted[event["DTSTART"].date()].append(event)

        pos_y = layout_h[0]
        for event_category in events_sorted:
            evt_nb = len(events_sorted[event_category])
            fillin = 0
            fillin_date = 0
            line_horiz_w = layout_w[0]+2
            if event_category == "Now":
                fillin = 255
                fillin_date = 255
                black_back = round_rect((layout_w[1]-layout_w[0], evt_nb*event_h),
                                        event_h_half, 0, '0011')
                mask = round_rect((layout_w[1]-layout_w[0], evt_nb*event_h),
                                  event_h_half, 255, '0011')
                Image_global.paste(black_back, (layout_w[0], pos_y), mask)
            elif event_category == "Today":
                line_horiz_w += date_w-4
                fillin = 0
                fillin_date = 255
                black_back = round_rect((date_w-2, evt_nb*event_h),
                                        event_h_half, 0, '1101')
                mask = round_rect((date_w-2, evt_nb*event_h),
                                  event_h_half, 255, '1101')
                Image_global.paste(black_back, (layout_w[0], pos_y), mask)
            else:
                Image_Draw.line((layout_w[0]+1, pos_y+event_h_half, layout_w[0]+1, pos_y+evt_nb*event_h),
                                fill=fillin)  # draw vertical line for all event of the day

            for index, event in enumerate(events_sorted[event_category]):
                time_start = event["DTSTART"]
                last = index == (evt_nb-1)
                date_draw = ''
                if index == 0:  # if first
                    if isinstance(event_category, str):
                        date_draw = event_category
                    else:
                        date_draw = event_category.strftime("%a")
                elif time_start.strftime("%H%M") != "0000":
                    date_draw = time_start.strftime("%H:%M")
                if last:
                    Image_Draw.line((line_horiz_w, pos_y+event_h, layout_w[1]-45, pos_y+event_h),
                                    fill=fillin)  # draw horizontal bar if last event

                Image_Draw.text((layout_w[0]+4, pos_y), date_draw,
                                font=self.font_time_xs, fill=fillin_date)  # draw the start time
                if 'TODO' in event.keys():
                    if event['TODO']:
                        Image_global.paste(self.homework_icon, (layout_w[1] - 30, pos_y))
                event["SUMMARY"] = cut_text_to_length(Image_Draw, event["SUMMARY"],
                                                      self.font_time_xs,
                                                      layout_w[1]-date_w,
                                                      sum_char)
                Image_Draw.text((layout_w[0]+date_w, pos_y),
                                event["SUMMARY"], font=self.font_time_xs, fill=fillin)
                pos_y += event_h  # must be at the end

    def draw_tasks(self, Image_Draw, Image_global):
        layout_w = (190, 400)
        layout_h = (62, 480)
        task_h = 26
        task_h_half = int(task_h/2)
        # Image_Draw.line((layout_w[1], layout_h[0], layout_w[1], layout_h[1]), width=2, fill=0)
        title_char = 8
        tasks = json.loads(open("/home/pi/AlarmClockProject/AlarmClock/cache/ggtasks/tasks.json", "r").read())
        pos_y = layout_h[0]
        pos_x = layout_w[0] + 4
        for task_list_title in tasks:
            black_back = round_rect((layout_w[1]-layout_w[0], task_h),
                                    task_h_half, 0, '1111')
            mask = round_rect((layout_w[1]-layout_w[0], task_h),
                              task_h_half, 255, '1111')
            Image_global.paste(black_back, (layout_w[0], pos_y), mask)
            Image_Draw.text((pos_x+20, pos_y),
                            cut_text_to_length(Image_Draw, task_list_title,
                                               self.font_time_xs, layout_w[1] - pos_x,
                                               title_char),
                            font=self.font_time_xs, fill=255)
            pos_y += task_h

            task_list = tasks[task_list_title]
            for task_ in task_list:
                task = task_list[task_]

                Image_Draw.text((pos_x, pos_y),
                                cut_text_to_length(Image_Draw, task[0]['title'],
                                                   self.font_time_xs, layout_w[1] - pos_x,
                                                   title_char),
                                font=self.font_time_xs, fill=0)
                pos_y += task_h
                if len(task) > 1:
                    for subtask in task[1:]:
                        Image_Draw.text((pos_x+20, pos_y),
                                        cut_text_to_length(Image_Draw, subtask['title'],
                                                           self.font_time_xs, layout_w[1] - (pos_x+20),
                                                           title_char),
                                        font=self.font_time_xs, fill=0)
                        pos_y += task_h

    def draw_image(self, Image_Draw, Image_global):
        image_width, image_height = self.image_bike.size
        Image_global.paste(self.image_bike, (800-image_width, 480-image_height))

    def refresh(self):
        logging.info("Initialising display")
        self.epd.init()
        logging.info("Computing image")
        Image = Image_class.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
        Draw = ImageDraw.Draw(Image)
        display_func = [self.draw_weather,
                        self.draw_time,
                        # self.draw_image,
                        self.draw_calendar,
                        self.draw_tasks,
                        ]
        error_lines = 0
        for function in display_func:
            try:
                function(Draw, Image)
            except Exception as e:
                error_message = f"Error occured with :{function.__name__} \n {e}"
                display_error(Draw, (260, 60+error_lines*30), error_message)
                error_lines += 2
                print(error_message)
        if self.invert:
            Image = ImageOps.mirror(Image)  # Mirror image in horizontal axis
            # Image = Image.convert('L')  # Convert image to something invertable
            # Image = ImageOps.invert(Image)  # Invert BW image
            # Image = Image.convert('1')  # convert back to BlackWhite
        logging.info("Sending image to display")
        self.epd.display(self.epd.getbuffer(Image))
        logging.info("Sleeping")
        self.epd.sleep()

    def exit(self):
        self.epd.Dev_exit()
        logging.info("Releasing EPD")


if __name__ == '__main__':
    dsp = Display()
    dsp.refresh()
