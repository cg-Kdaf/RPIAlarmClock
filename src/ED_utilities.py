import json

cache_file = '/home/pi/AlarmClockProject/AlarmClock/cache/calendars/' + 'cal_ed.json'


def store_calendar():
    from EcoleDirect import EcoleDirect

    file_path = f"/home/pi/credentials/EcoleDirecte/credentials.txt"
    # file as following : 'id:user\npwd:password
    creds = open(file_path, "r").read().split("\n")
    user = creds[0].split(':')[1]
    pwd = creds[1].split(':')[1]

    ed = EcoleDirect(user, pwd)
    homeworks = ed.getHW()  # Get HomeWork
    calendar = ed.getWT()  # Get WorkTime
    # notes = ed.getNotes()  # Get Notes

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


if __name__ == "__main__":
    store_calendar()
