#!/usr/bin/python3
import epd7in5_V2
import logging
import json
from PIL import Image as Image_class, ImageDraw, ImageFont, ImageOps
from datetime import datetime
from calendars import get_calendar_sorted
from weather import get_weather_data
from news_utilities import get_news
from music_commands import Music_lib
from os import system as os_system


phone_ip = '192.168.1.41'
# logging.basicConfig(level=logging.DEBUG)


def device_status():
    response = os_system("ping -A -q -w 1 " + "192.168.1.42" + '> /dev/null')
    computer = int(response) == 0
    response = os_system("ping -A -q -w 1 " + phone_ip + '> /dev/null')
    phone = int(response) == 0
    return (computer, phone)


def add_tuple(tuple1, tuple2):
    return tuple(map(sum, zip(tuple1, tuple2)))


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
    d.text((0, 0), text_,  font=font_, fill=fill_)
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
    mask = Image_class.new('1', size, 255)
    corner = round_corner(radius, 255)
    if corners[0] == '1':
        mask.paste(corner, (0, 0))
    if corners[3] == '1':
        mask.paste(corner.rotate(90), (0, height - radius))  # Rotate the corner and paste it
    if corners[2] == '1':
        mask.paste(corner.rotate(180), (width - radius, height - radius))
    if corners[1] == '1':
        mask.paste(corner.rotate(270), (width - radius, 0))
    return rectangle, mask


def display_error(Image_Draw, xy, error_str):
    font_ = ImageFont.truetype('data/Teko/Teko-Light.ttf', 32)
    Image_Draw.text(xy, error_str, font=font_, fill=0)


def font(path, size, extansion=None):
    if isinstance(path[0], str):
        path = f"{path[0].split('.')[0]}-{extansion}.{path[0].split('.')[1]}"
    return ImageFont.truetype(path, size)


class Display():
    def __init__(self):
        logging.info("Creating EPD (ElectronicPaperDisplay) object")
        self.ring_icon = Image_class.open('data/bell.bmp')
        self.homework_icon = Image_class.open('data/homework.bmp')
        self.image_bike = Image_class.open('data/image_bike.bmp')

        self.font_weather = 'data/weather_font.ttf'
        self.font_teko = ['data/Teko/Teko.ttf',
                          'Light', 'Bold', 'Medium', 'Regular', 'SemiBold']
        self.font_tulpenone = 'data/Tulpen_One/TulpenOne-Regular.ttf'
        self.font_orbitron = ['data/Orbitron/static/Orbitron.ttf',
                              'Black', 'Bold', 'ExtraBold', 'Medium', 'Regular', 'SemiBold']
        self.font_balsamiq = ['data/Balsamiq_Sans/BalsamiqSans.ttf',
                              'BoldItalic', 'Bold', 'Italic', 'Regular']
        self.font_monoton = 'data/Monoton/Monoton-Regular.ttf'
        self.happening_events = []

        self.invert = False
        self.interval = 0
        self.minimal = False

        self.epd = epd7in5_V2.EPD()

    def draw_time(self, Image_Draw, Image_global):
        layout_w = (0, 330)
        layout_h = (0, 60)
        time_font = font(self.font_orbitron, 64, 'Regular')
        date_font = font(self.font_orbitron, 24, 'SemiBold')

        # Separator bottom
        Image_Draw.line((layout_w[0], layout_h[1], layout_w[1], layout_h[1]), width=4, fill=0)
        # Separator right
        Image_Draw.line((layout_w[1], layout_h[0], layout_w[1], layout_h[1]), width=2, fill=0)

        now = datetime.now()  # +timedelta(minutes=round((self.interval/60-1)/2))

        # Draw date
        date_text = now.strftime("%-d%b")  # Date as 1Jan
        text1_w, text1_h = Image_Draw.textsize(date_text, font=date_font)
        Image_Draw.text((layout_w[1]-text1_w, layout_h[0]), date_text, font=date_font, fill=0)

        # Draw interval
        if self.interval != 0:
            interval_text = str(int(self.interval/60))+"min"
            text2_w, text2_h = Image_Draw.textsize(interval_text, font=date_font)
            Image_Draw.text((layout_w[1]-text2_w, (layout_h[1]+layout_h[0])/2),
                            interval_text, font=date_font, fill=0)

        # Draw time
        time_text = now.strftime("%k:%M")  # Time as 14:03 or 3:50
        text3_w, text3_h = Image_Draw.textsize(time_text, font=time_font)
        Image_Draw.text(((layout_w[0]+layout_w[1]-text1_w-text3_w)/2, layout_h[0]-15),
                        time_text, font=time_font, fill=0)

    def draw_weather(self, Image_Draw, Image_global):
        now = datetime.now()
        layout_w = (480, 800)
        layout_h = (0, 60)

        date_font = font(self.font_teko, 24, 'Medium')

        # Separator bottom
        Image_Draw.line((layout_w[0], layout_h[1], layout_w[1], layout_h[1]), width=4, fill=0)

        start_day = datetime(2000, 1, 1, 5)
        end_day = datetime(2000, 1, 1, 22)
        weather_data = {}
        for index, data in enumerate(get_weather_data()):
            time_datetime = datetime.strptime(data["dt_txt"], '%Y-%m-%d %H:%M:%S')
            date_str = str(time_datetime.date())

            if time_datetime.time() > end_day.time() or time_datetime.time() < start_day.time():
                continue
            if date_str not in weather_data.keys():
                weather_data[date_str] = data
            else:
                temp_min = min(data["main"]["temp_min"], weather_data[date_str]["main"]["temp_min"])
                weather_data[date_str]["main"]["temp_min"] = temp_min
                temp_max = max(data["main"]["temp_max"], weather_data[date_str]["main"]["temp_max"])
                weather_data[date_str]["main"]["temp_max"] = temp_max
        for index_day, day in enumerate(weather_data):
            pos_x = layout_w[0]+80*index_day
            date = datetime.strptime(day, '%Y-%m-%d')
            if now.date() == date.date():
                date_text = "Today"
            else:
                date_text = cut_text_to_length(Image_Draw, date.strftime('%A'), date_font, 55, 5)
            draw_text_angle(Image_Draw, Image_global, (pos_x+4, 0), date_text, date_font, 90)
            for index_part, prop in enumerate(["temp_min", "temp_max"]):
                pos_y = index_part*30
                Image_Draw.text((pos_x + 30, pos_y),
                                f'{round(weather_data[day]["main"][prop])}°',
                                font=font(self.font_teko, 26, 'Medium'), fill=0)

    def draw_calendar(self, Image_Draw, Image_global):
        self.happening_events = []
        layout_w = (0, 180)
        layout_h = (62, 480)

        font_event = font(self.font_teko, 26, 'Medium')

        # Image_Draw.line((layout_w[1], layout_h[0], layout_w[1], layout_h[1]), width=2, fill=0)
        event_h = 28
        event_h_half = int(event_h/2)
        date_w = 58
        sum_char = 14
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
                black_back, mask = round_rect((layout_w[1]-layout_w[0], evt_nb*event_h),
                                              event_h_half, 0, '0011')
                Image_global.paste(black_back, (layout_w[0], pos_y), mask)
            elif event_category == "Today":
                line_horiz_w += date_w-4
                fillin = 0
                fillin_date = 255
                black_back, mask = round_rect((date_w-2, evt_nb*event_h),
                                              event_h_half, 0, '1101')
                Image_global.paste(black_back, (layout_w[0], pos_y), mask)
            else:
                Image_Draw.line((layout_w[0]+1,
                                 pos_y+event_h_half, layout_w[0]+1, pos_y+evt_nb*event_h),
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
                                font=font_event, fill=fillin_date)  # draw the start time
                if 'TODO' in event.keys():
                    if event['TODO']:
                        mask = self.homework_icon.convert('L')
                        mask = ImageOps.invert(mask)  # Invert BW image
                        mask = mask.convert('1')  # convert back to Binary image
                        Image_global.paste(self.homework_icon, (layout_w[1] - 30, pos_y), mask)
                event["SUMMARY"] = cut_text_to_length(Image_Draw, event["SUMMARY"],
                                                      font_event,
                                                      layout_w[1]-date_w,
                                                      sum_char)
                Image_Draw.text((layout_w[0]+date_w, pos_y),
                                event["SUMMARY"], font=font_event, fill=fillin)
                pos_y += event_h  # must be at the end

    def draw_tasks(self, Image_Draw, Image_global):
        layout_w = (190, 400)
        layout_h = (62, 480)

        font_task = font(self.font_teko, 26, 'Medium')

        task_h = 28
        task_h_half = int(task_h/2)
        # Image_Draw.line((layout_w[1], layout_h[0], layout_w[1], layout_h[1]), width=2, fill=0)
        title_char = 8
        json_file = "/home/pi/AlarmClockProject/AlarmClock/cache/ggtasks/tasks.json"
        tasks = json.loads(open(json_file, "r").read())
        pos_y = layout_h[0]
        pos_x = layout_w[0] + 4
        for task_list_title in tasks:
            black_back, mask = round_rect((layout_w[1]-layout_w[0], task_h),
                                          task_h_half, 0, '1111')
            Image_global.paste(black_back, (layout_w[0], pos_y), mask)
            Image_Draw.text((pos_x+20, pos_y),
                            cut_text_to_length(Image_Draw, task_list_title,
                                               font_task, layout_w[1] - pos_x,
                                               title_char),
                            font=font_task, fill=255)
            pos_y += task_h

            task_list = tasks[task_list_title]
            for task_ in task_list:
                task = task_list[task_]

                Image_Draw.text((pos_x, pos_y),
                                cut_text_to_length(Image_Draw, task[0]['title'],
                                                   font_task, layout_w[1] - pos_x,
                                                   title_char),
                                font=font_task, fill=0)
                pos_y += task_h
                if len(task) > 1:
                    Image_Draw.line((layout_w[0]+8, pos_y,
                                     layout_w[0]+8, pos_y + (len(task)-1) * task_h),
                                    width=2, fill=0)
                    for subtask in task[1:]:
                        Image_Draw.text((pos_x+20, pos_y),
                                        cut_text_to_length(Image_Draw, subtask['title'],
                                                           font_task, layout_w[1] - (pos_x+20),
                                                           title_char),
                                        font=font_task, fill=0)
                        pos_y += task_h

    def draw_news(self, Image_Draw, Image_global):
        layout_w = (415, 800)
        layout_h = (62, 480)
        news_h = 30
        news_subline_h = 22
        news = get_news()
        pos_y = layout_h[0]
        for news_index in news.keys():
            Image_Draw.text((layout_w[0], pos_y), news[news_index]['title']+' :',
                            font=font(self.font_orbitron, 28, 'Black'), fill=0)
            pos_y += news_h
            for line in news[news_index]['desc'].split('\n'):
                if not line.strip():
                    continue
                Image_Draw.text((layout_w[0]+8, pos_y), line,
                                font=font(self.font_orbitron, 20, 'ExtraBold'), fill=0)
                pos_y += news_subline_h

    def draw_image(self, Image_Draw, Image_global):
        image_width, image_height = self.image_bike.size
        Image_global.paste(self.image_bike, (800-image_width, 480-image_height))

    def draw_minimal(self, Image_Draw, Image_global):
        layout_w = (0, 800)
        layout_h = (0, 480)
        time_font = font(self.font_orbitron, 200, 'Regular')
        date_font = font(self.font_orbitron, 48, 'SemiBold')

        now = datetime.now()

        # Draw a widget for the Alarm
        is_alarm_on = open("/home/pi/AlarmClockProject/AlarmClock/cache/alarm_status", "r").read()
        if "1" in is_alarm_on:
            Image_global.paste(self.ring_icon, (layout_w[0], layout_h[0]))

        # Draw time
        time_text = now.strftime("%k:%M")  # Time as 14:03 or 3:50
        text_w, text_h = time_font.getbbox(time_text, anchor="lt")[2:]
        text_pos = (int((layout_w[0]+layout_w[1]-text_w)/2),
                    120)
        text_size = (text_w, text_h)

        rectangle1_pos = add_tuple(text_pos, (-30, -30))
        rectangle1_size = add_tuple(text_size, (60, 60))
        back_rectangle, mask = round_rect(rectangle1_size, 40, 0)
        Image_global.paste(back_rectangle, rectangle1_pos, mask)

        rectangle2_pos = add_tuple(text_pos, (-20, -20))
        rectangle2_size = add_tuple(text_size, (40, 40))
        back_rectangle, mask = round_rect(rectangle2_size, 30, 255)
        Image_global.paste(back_rectangle, rectangle2_pos, mask)

        Image_Draw.text(text_pos,
                        time_text, fill=0, anchor="lt", font=time_font)

        # Draw date
        date_text = now.strftime("%A %-d %B %G")  # Date as Monday 1 Jan 2000
        text_w, text_h = Image_Draw.textsize(date_text, font=date_font)
        text_pos = (int((layout_w[0]+layout_w[1])/2),
                    add_tuple(rectangle1_pos, rectangle1_size)[1]+4)
        Image_Draw.text(text_pos, date_text, fill=0, anchor="mt", font=date_font)

        # Draw music status
        mocp = Music_lib()
        infos = mocp.get_status_mocp()
        if infos != {}:
            if 'SongTitle' in infos.keys():
                music_text = f"{infos['SongTitle'].split('(')[0]} // {infos['Artist']}"
            else:
                music_text = "Music stopped"
            if infos['State'] == 'PAUSE':
                music_text += ' / PAUSED'
        else:
            music_text = "Mocp not running"
        text_w, text_h = Image_Draw.textsize(music_text, font=date_font)
        text_pos = add_tuple(text_pos, (0, 40))
        Image_Draw.text(text_pos, music_text, fill=0, anchor="mt", font=date_font)

        # Draw a widget for the Alarm
        if "1" in is_alarm_on:
            alarm_status = "Alarm ON"
        else:
            alarm_status = "Alarm OFF"
        text_w, text_h = Image_Draw.textsize(alarm_status, font=date_font)
        text_pos = add_tuple(text_pos, (0, 40))
        Image_Draw.text(text_pos, alarm_status, fill=0, anchor="mt", font=date_font)

    def draw_music_devices_status(self, Image_Draw, Image_global):
        layout_w = (330, 480)
        layout_h = (0, 60)

        font_music = font(self.font_teko, 26, 'Medium')

        # Separator bottom
        Image_Draw.line((layout_w[0], layout_h[1], layout_w[1], layout_h[1]), width=4, fill=0)
        # Separator right
        Image_Draw.line((layout_w[1], layout_h[0], layout_w[1], layout_h[1]), width=2, fill=0)

        mocp = Music_lib()
        infos = mocp.get_status_mocp()
        if infos != {}:
            if infos['State'] == 'PAUSE':  # Add a Pause icon
                rectangle1_pos = add_tuple((layout_w[0], layout_h[0]), (8, 3))
                rectangle1_size = (5, 24)
                back_rectangle, mask = round_rect(rectangle1_size, 2, 0)
                Image_global.paste(back_rectangle, rectangle1_pos, mask)

                rectangle1_pos = add_tuple(rectangle1_pos, (12, 0))
                back_rectangle, mask = round_rect(rectangle1_size, 2, 0)
                Image_global.paste(back_rectangle, rectangle1_pos, mask)
            elif infos['State'] == 'PLAY':  # Add a Play icon
                point1 = add_tuple((layout_w[0], layout_h[0]), (8, 3))
                point2 = add_tuple(point1, (0, 24))
                point3 = add_tuple((layout_w[0], layout_h[0]), (20, 3+12))
                Image_Draw.polygon([point1, point2, point3], fill=0)
            else:
                rectangle1_pos1 = add_tuple((layout_w[0], layout_h[0]), (8, 6))
                rectangle1_pos2 = add_tuple((layout_w[0], layout_h[0]), (25, 23))
                Image_Draw.rectangle([rectangle1_pos1, rectangle1_pos2], fill=0)
            if 'SongTitle' in infos.keys():
                music_text = infos['SongTitle'].split("(")[0]
            else:
                music_text = "Music stopped"
        else:
            music_text = "Mocp not running"

        text_pos = (layout_w[0]+30, layout_h[0]-2)
        text_length = layout_w[1]-30-text_pos[0]
        music_text = cut_text_to_length(Image_Draw, music_text, font_music, text_length, 6)
        Image_Draw.text(text_pos, music_text, fill=0, anchor="la", font=font_music)

        # Draw a widget for the Alarm
        is_alarm_on = open("/home/pi/AlarmClockProject/AlarmClock/cache/alarm_status", "r").read()
        alarm_status = "Alarm OFF"
        if "1" in is_alarm_on:
            Image_global.paste(self.ring_icon, (layout_w[0]+3, layout_h[1]-30))
            alarm_status = "Alarm ON"
        text_pos = add_tuple(text_pos, (3, 28))
        Image_Draw.text(text_pos, alarm_status, fill=0, anchor="la", font=font_music)
        is_computer, is_phone = device_status()
        if is_phone:
            rectangle_pos = add_tuple((layout_w[1], layout_h[0]), (-22, 2))
            rectangle_size = (14, 26)
            back_rectangle, mask = round_rect(rectangle_size, 3, 0)
            Image_global.paste(back_rectangle, rectangle_pos, mask)

            rectangle_pos = add_tuple(rectangle_pos, (3, 3))
            rectangle_size = (8, 20)
            back_rectangle, mask = round_rect(rectangle_size, 2, 255)
            Image_global.paste(back_rectangle, rectangle_pos, mask)
        if is_computer:
            rectangle_pos = add_tuple((layout_w[1], layout_h[0]), (-28, 32))
            rectangle_size = (26, 18)
            back_rectangle, mask = round_rect(rectangle_size, 3, 0)
            Image_global.paste(back_rectangle, rectangle_pos, mask)

            rectangle_pos = add_tuple(rectangle_pos, (3, 3))
            rectangle_size = (20, 12)
            back_rectangle, mask = round_rect(rectangle_size, 2, 255)
            Image_global.paste(back_rectangle, rectangle_pos, mask)

            rectangle_pos = add_tuple((layout_w[1], layout_h[0]), (-20, 32+18))
            rectangle_size = (10, 6)
            back_rectangle, mask = round_rect(rectangle_size, 3, 0)
            Image_global.paste(back_rectangle, rectangle_pos, mask)

    def refresh(self):
        logging.info("Initialising display")
        self.epd.init()
        logging.info("Computing image")
        Image = Image_class.new('1', (self.epd.width, self.epd.height), 255)  # 255: clear the frame
        Draw = ImageDraw.Draw(Image)
        display_func = [
                        self.draw_weather,
                        self.draw_music_devices_status,
                        self.draw_time,
                        # self.draw_image,
                        self.draw_calendar,
                        self.draw_tasks,
                        self.draw_news,
                        ]
        if self.minimal:
            display_func = [self.draw_minimal]
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


if __name__ == '__main__':
    dsp = Display()
    dsp.refresh()
