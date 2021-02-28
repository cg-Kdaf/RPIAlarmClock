import json
from datetime import datetime, timedelta
from news_utilities import add_news

cache_file = '/home/pi/AlarmClockProject/AlarmClock/cache/calendars/' + 'cal_ed.json'

homeworks = None
calendar = None
notes = None
datetime_now = datetime.now()


def str_to_datetime(date_str):
    if len(date_str) == 16:
        datetime_time = datetime(int(date_str[:4]),  # Year
                                 int(date_str[5:7]),  # Month
                                 int(date_str[8:10]),  # Day
                                 int(date_str[11:13]),  # Hour
                                 int(date_str[14:16]))  # Minute
    else:
        datetime_time = datetime(int(date_str[:4]),  # Year
                                 int(date_str[5:7]),  # Month
                                 int(date_str[8:10]))  # Day
    return(datetime_time)


def get_ed_data():
    global homeworks, calendar, notes
    from EcoleDirect import EcoleDirect

    file_path = f"/home/pi/credentials/EcoleDirecte/credentials.txt"
    # file as following : 'id:user\npwd:password
    creds = open(file_path, "r").read().split("\n")
    user = creds[0].split(':')[1]
    pwd = creds[1].split(':')[1]

    ed = EcoleDirect(user, pwd)
    homeworks = ed.getHW()  # Get HomeWork
    calendar = ed.getWT()  # Get WorkTime
    notes = ed.getNotes()  # Get Notes


def store_calendar():
    if any(data is None for data in [homeworks, calendar, notes]):
        get_ed_data()

    home_works = []
    for work_day in homeworks:
        for work in homeworks[work_day]:
            code = work['codeMatiere']
            if not work['effectue']:
                home_works.append([code, work_day])

    events = []
    for lesson in calendar:
        dtstart = lesson['start_date']
        dtend = lesson['end_date']
        summary = lesson['codeMatiere']
        if any(dtstart[:10] == work[1] and summary == work[0] for work in home_works):
            todo = True
        else:
            todo = False
        event = {'DTSTART': dtstart,
                 'DTEND': dtend,
                 'SUMMARY': summary,
                 'TODO': todo,
                 'CAL_ID': '200'}
        events.append(event)

    # Store the events in a new calendar file
    with open(cache_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(events, jsonfile, ensure_ascii=False, indent=4)


def get_calendar():
    events = json.loads(open(cache_file, "r").read())
    return events


def get_latest_notes():
    if any(data is None for data in [homeworks, calendar, notes]):
        get_ed_data()

    last_n_days = 10
    notes_ = sorted(notes['notes'], key=lambda i: i['dateSaisie'])
    news_desc = ''
    for note in notes_:
        saisie_time = str_to_datetime(note['dateSaisie'])
        if saisie_time < datetime_now-timedelta(days=last_n_days):
            continue
        individual_note = note['valeur']
        class_avg = note['moyenneClasse']

        better_than_class = individual_note > class_avg
        note_str = f"{individual_note}/{note['noteSur']}"
        subject = note['codeMatiere']
        news_desc += f"\{subject}: {note_str} {'+' if better_than_class else '-'}  "
    add_news(300, datetime_now, 'Latest notes', news_desc)


if __name__ == "__main__":
    # store_calendar()
    get_latest_notes()
