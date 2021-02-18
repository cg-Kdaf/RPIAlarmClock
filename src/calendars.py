from datetime import datetime, timedelta

wanted_params = ["DTSTART",
                 "DTEND",
                 "SUMMARY",
                 "RRULE",
                 "EXDATE",
                 "BEGIN:VEVENT",
                 "END:VEVENT"]
dates_lines = ["DTSTART",
               "DTEND",
               "EXDATE"]
needed_params = ["DTSTART",
                 "DTEND",
                 "SUMMARY"]


def get_event_from_text(file_index, exclude_passed=True):
    '''Get events upcomming from a ics textfile'''
    # timenow = arrow_now().format("YYYYMMDDTHHmmss")+"Z"

    events = []
    in_event = False
    event_index = -1

    file_path = f"/home/pi/AlarmClockProject/AlarmClock/cache/calendars/calendar{file_index}.ics"
    calendar_file = open(file_path, "r").readlines()

    def str_to_datetime(date_str):
        datetime_time = None
        if len(date_str) > 10:  # parsing datetime like 20191031T225959(Z)
            datetime_time = datetime(int(date_str[:4]),  # Year
                                     int(date_str[4:6]),  # Month
                                     int(date_str[6:8]),  # Day
                                     int(date_str[9:11]),  # Hour
                                     int(date_str[11:13]),  # Minute
                                     int(date_str[13:15]))  # Second
            if "Z" in date_str:
                datetime_time += timedelta(hours=1)
        else:  # parsing datetime like 20191031
            datetime_time = datetime(int(date_str[:4]),  # Year
                                     int(date_str[4:6]),  # Month
                                     int(date_str[6:8]),  # Day
                                     0,
                                     0,
                                     0)
        return(datetime_time)

    # ||| Parsing Calendar and create all events, no matter if they're from past ||||
    for line in calendar_file:
        if "BEGIN:VEVENT" in line:  # Create new event when begin detected
            events.append({})  # Create the new event
            event_index += 1  # Increse index for each event
            in_event = True  # Used to know if the line is part of the event
            continue

        if not in_event:  # Go next line if not in event
            continue

        # If line is not valid, or start with a space, go next line
        line = line.replace("\n", '')
        if ":" not in line:
            continue

        if not any(x in line for x in wanted_params):
            # Go next line if word detected, used to hide unwanted props
            continue

        # Split line with attribute name and attribute value
        terms = line.split(":")
        is_summary = terms[0] == 'SUMMARY'

        if terms[1] in [' ', '']:
            if is_summary:
                events.pop()
                event_index -= 1
                in_event = False
            continue

        if ";" in terms[0]:
            terms[0] = terms[0].split(";")[0]

        if "=" in terms[1] and not is_summary:
            value_new = {}
            for elt in terms[1].split(';'):
                key, value = elt.split('=')
                if len(value) in [8, 15, 16]:
                    value = str_to_datetime(value)
                value_new[key] = value
            terms[1] = value_new

        if "END:VEVENT" in line:  # Finalize event when end reached
            if any(x not in events[event_index].keys() for x in needed_params):
                events.pop()
                event_index -= 1
            in_event = False
            events[event_index]["CAL_ID"] = file_index
            continue

        if any(x in terms[0] for x in dates_lines):
            terms[1] = str_to_datetime(terms[1])

        if terms[0] in events[event_index].keys():
            if not isinstance(events[event_index][terms[0]], list):
                content = events[event_index][terms[0]]
                events[event_index][terms[0]] = []
                events[event_index][terms[0]].append(content)
            events[event_index][terms[0]].append(terms[1])
        else:
            events[event_index][terms[0]] = terms[1]

    if not exclude_passed:
        return events

    # ||| Check if events are from past, then delete them |||
    datetime_now = datetime.now()
    events_comming = []
    for event in events:
        params = event.keys()
        if "RRULE" in params:
            rrules = event["RRULE"]
            if 'FREQ' not in rrules.keys():
                continue
            if 'UNTIL' in rrules.keys():
                if rrules['UNTIL'] < datetime_now:
                    continue

            if rrules['FREQ'] == "WEEKLY":
                event_duration = event["DTEND"] - event["DTSTART"]
                week_day_event_end = event['DTEND'].weekday()
                difference = week_day_event_end-datetime_now.weekday()
                if (difference < 0 or
                   (difference == 0 and event['DTEND'].time() < datetime_now.time())):
                    difference += 7
                if 'INTERVAL' in rrules.keys():
                    interval = int(rrules['INTERVAL'])
                    days_difference = (datetime_now-event['DTEND']).days
                    weeks_elapsed = int(days_difference/7)+1
                    weeks_difference = weeks_elapsed % interval
                    difference += (weeks_difference)*7
                event["DTEND"] = (datetime(datetime_now.year,
                                           datetime_now.month,
                                           datetime_now.day,
                                           event['DTEND'].hour,
                                           event['DTEND'].minute,
                                           event['DTEND'].second)
                                  + timedelta(days=difference))
                event["DTSTART"] = event["DTEND"] - event_duration
                if "EXDATE" in params:
                    if not isinstance(event["EXDATE"], list):
                        event["EXDATE"] = [event["EXDATE"]]
                    while event["DTSTART"] in event["EXDATE"]:
                        if 'INTERVAL' in rrules.keys():
                            event["DTSTART"] += timedelta(weeks=int(rrules['INTERVAL']))
                        else:
                            event["DTSTART"] += timedelta(weeks=1)
            elif rrules['FREQ'] == "YEARLY":
                for param_to_change in ['DTSTART', 'DTEND']:
                    time_to_change = event[param_to_change]
                    event[param_to_change] = datetime(datetime_now.year,
                                                      time_to_change.month,
                                                      time_to_change.day,
                                                      time_to_change.hour,
                                                      time_to_change.minute,
                                                      time_to_change.second)
        event["STATUS"] = 0
        event["STATUS"] += event["DTSTART"] < datetime_now
        event["STATUS"] += event["DTEND"] < datetime_now
        if event["STATUS"] == 2:
            continue
        events_comming.append(event)
    return events_comming


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
    for event in get_calendar_sorted(range(4))[:20]:
        print(event)
