#!/usr/bin/python3
# from arrow import now as arrow_now, get as arrow_get
from datetime import datetime, timedelta


def get_event_from_text(file_index, exclude_passed=True):
    '''Get events upcomming from a ics textfile'''
    # timenow = arrow_now().format("YYYYMMDDTHHmmss")+"Z"
    week_day_now = datetime.now().weekday()
    datetime_now = datetime.now()

    events = []
    in_event = False
    weekly = False
    exdate_id = 0
    field_empty = 0
    event_index = -1

    file_path = f"/home/pi/AlarmClockProject/AlarmClock/cache/calendars/calendar{file_index}.ics"
    calendar_file = open(file_path, "r")

    for line in calendar_file:
        # If line is not valid, or start by a space, go next line
        if (":" not in line) or (line[0] == " "):
            continue
        line = line.replace("\n", '')
        # Split line with attribute name and attribute value
        terms = line.split(":")
        print(terms)

        if "BEGIN:VEVENT" in line:  # Create new event when begin detected
            events.append({})  # Create the new event
            event_index += 1  # Increse index for each event
            field_empty = 0  # Used to count the empty fields
            exdate_id = 0  # Used to count the exdates of an event

            # STATUS is 0 if event is comming, 1 if event is happening, and 2 if event happened
            events[event_index]["STATUS"] = 0
            in_event = True  # Used to know if the line is part of the event
            continue

        if not in_event:  # Go next line if not in event
            continue

        if "END:VEVENT" in line:  # Finalize event when end reached
            if weekly:
                week_day_event = time_.weekday()
                difference = week_day_event-week_day_now
                if difference < 0:
                    difference += 7
                if 'DTSTART' in events[event_index].keys():
                    events[event_index]['DTSTART'] += timedelta(days=difference)
                if 'DTEND' in events[event_index].keys():
                    events[event_index]['DTSTART'] += timedelta(days=difference)
            else:
                if events[event_index]['DTSTART'] < datetime_now:
                    events[event_index]["STATUS"] += 1
                if events[event_index]['DTEND'] < datetime_now:
                    events[event_index]["STATUS"] += 1
                if exclude_passed:
                    if events[event_index]["STATUS"] == 2:
                        events.pop()
                        event_index -= 1
                        field_empty = 0
            in_event = False
            continue

        if ("DTSTAMP" in line) or ("MODIFIED" in line) or ("TRANSP" in line) or ("CREAT" in line) or ("STATUS" in line) or ("SEQUENCE" in line) or ("APPLE" in line) : # Go next line if word detected, used to hide unwanted props
            continue

        if terms[1] == " ":  # If attribute value is empty count it
            field_empty += 1

        if (field_empty > 1) or ((events[event_index]["STATUS"] == 2) and exclude_passed):  # If too many filds are empty or if event passed, delete event
            events.pop()
            event_index -= 1
            field_empty = 0
            in_event = False
            continue

        if ("DTSTART" in line) or ("DTEND" in line):

            if ";" in line:
                terms[0] = line.split(";")[0]

            if len(terms[1]) > 10:
                if "Z" in terms[1]:
                    time_ = datetime.strptime(terms[1], "%Y%m%dT%H%M%SZ") + timedelta(hours=1)
                else:
                    time_ = datetime.strptime(terms[1], "%Y%m%dT%H%M%S")
            else:
                time_ = datetime.strptime(terms[1], "%Y%m%d")

            terms[1] = time_

        if "EXDATE" in line:
            if ";" in line:
                terms[0] = line.split(";")[0]
            if "EXDATE" in ''.join(events[event_index].keys()):
                exdate_id += 1
            terms[0] = f"{exdate_id}EXDATE"
            if len(terms[1]) > 10:
                if "Z" in terms[1]:
                    time_ = datetime.strptime(terms[1], "%Y%m%dT%H%M%SZ") + timedelta(hours=1)
                else:
                    time_ = datetime.strptime(terms[1], "%Y%m%dT%H%M%S")
            else:
                time_ = datetime.strptime(terms[1], "%Y%m%d")
            if time_ == events[event_index]["DTSTART"]
            terms[1] = time_

        if ("FREQ" in line) and ("WEEKLY" in line):
            weekly = True

        events[event_index][terms[0]] = terms[1]  # Append attribute to event
    return events


def sort_events(events, attribute="DTSTART"):
    ''' Sort event by attribute, default DTSTART'''
    return sorted(events, key=lambda i: i[attribute])


def get_calendar_sorted(index, exclude_passed=True):
    if isinstance(index, int):
        sorted_events = sort_events(get_event_from_text(index, exclude_passed))
    else:
        events = []
        for index_ in index:
            events += get_event_from_text(index_, exclude_passed)
        sorted_events = sort_events(events)
    return sorted_events


if __name__ == "__main__":
    for event in get_calendar_sorted(3, True):
        print(event)
        # pass
