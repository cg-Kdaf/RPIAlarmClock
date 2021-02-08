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
    exdate_id = 0
    field_empty = 0
    event_index = -1

    file_path = f"/home/pi/AlarmClockProject/AlarmClock/cache/calendars/calendar{file_index}.ics"
    calendar_file = open(file_path, "r")

    def str_to_datetime(date_str):
        if len(date_str) > 10:
            if "Z" in date_str:
                return(datetime.strptime(date_str, "%Y%m%dT%H%M%SZ") + timedelta(hours=1))
            else:
                return(datetime.strptime(date_str, "%Y%m%dT%H%M%S"))
        else:
            return(datetime.strptime(date_str, "%Y%m%d"))

    for line in calendar_file:
        # If line is not valid, or start by a space, go next line
        if (":" not in line) or (line[0] == " "):
            continue
        line = line.replace("\n", '')
        # Split line with attribute name and attribute value
        terms = line.split(":")

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

        if ("DTSTAMP" in line) or ("MODIFIED" in line) or ("TRANSP" in line) or ("CREAT" in line) or ("STATUS" in line) or ("SEQUENCE" in line) or ("APPLE" in line) or ("UID" in line):  # Go next line if word detected, used to hide unwanted props
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

            terms[1] = str_to_datetime(terms[1])

        if "EXDATE" in line:
            if ";" in line:
                terms[0] = line.split(";")[0]
            if "EXDATE" in ''.join(events[event_index].keys()):
                exdate_id += 1
            terms[0] = f"{exdate_id}EXDATE"
            time_ = str_to_datetime(terms[1])
            if time_ == events[event_index]["DTSTART"]:
                field_empty += 2
            terms[1] = time_

        if ("RRULE" in line):
            rrules = {}
            for rrule in terms[1].split(';'):
                rrules[rrule.split('=')[0]] = rrule.split('=')[1]
            if 'FREQ' not in rrules.keys():
                continue
            if 'UNTIL' in rrules.keys():
                if str_to_datetime(rrules['UNTIL']) < datetime_now:
                    continue

            if rrules['FREQ'] == "WEEKLY":
                week_day_event = events[event_index]['DTSTART'].weekday()
                difference = week_day_event-week_day_now
                if difference < 0:
                    difference += 7
                if 'INTERVAL' in rrules.keys():
                    days_difference = (datetime_now-events[event_index]['DTSTART']).days
                    if not (days_difference/int(rrules['INTERVAL'])).is_integer():
                        continue
                    # if difference/rrules['INTERVAL']
                if 'DTSTART' in events[event_index].keys():
                    start_event = events[event_index]['DTSTART']
                    events[event_index]['DTSTART'] = datetime(datetime_now.year,
                                                              datetime_now.month,
                                                              datetime_now.day,
                                                              start_event.hour,
                                                              start_event.minute,
                                                              start_event.second) + timedelta(days=difference)
                if 'DTEND' in events[event_index].keys():
                    end_event = events[event_index]['DTSTART']
                    events[event_index]['DTEND'] = datetime(datetime_now.year,
                                                            datetime_now.month,
                                                            datetime_now.day,
                                                            end_event.hour,
                                                            end_event.minute,
                                                            end_event.second) + timedelta(days=difference)
            elif rrules['FREQ'] == "YEARLY":
                if 'DTSTART' in events[event_index].keys():
                    start_event = events[event_index]['DTSTART']
                    events[event_index]['DTSTART'] = datetime(datetime_now.year,
                                                              start_event.month,
                                                              start_event.day,
                                                              start_event.hour,
                                                              start_event.minute,
                                                              start_event.second)
                if 'DTEND' in events[event_index].keys():
                    end_event = events[event_index]['DTSTART']
                    events[event_index]['DTEND'] = datetime(datetime_now.year,
                                                            end_event.month,
                                                            end_event.day,
                                                            end_event.hour,
                                                            end_event.minute,
                                                            end_event.second)

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
    for event in get_calendar_sorted(2)[:20]:
        print(event)
        # pass
