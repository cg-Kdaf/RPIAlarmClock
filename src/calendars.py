#!/usr/bin/python3
from arrow import now as arrow_now,get as arrow_get
from datetime import datetime, timedelta

def get_event_from_text(file_index, exclude_passed = True, weekly = False):
    '''Get events upcomming from a ics textfile'''
    timenow = arrow_now().format("YYYYMMDDTHHmmss")+"Z"
    day_time_now = datetime.now().time()
    week_day_now = datetime.now().weekday()
    datetime_now = datetime.now()
    
    events=[]
    in_event = False
    field_empty = 0
    event_index = -1
    
    file_path = f"/home/pi/AlarmClockProject/AlarmClock/cache/calendars/calendar{file_index}.ics"
    calendar_file = open(file_path, "r")
    
    for line in calendar_file:
        if (not ":" in line) or (line[0] == " "): # If line is not valid, or start by a space, go next line
            continue
        
        terms=line.split(":") # Split line with attribute name and attribute value
        
        if "BEGIN:VEVENT" in line : # Create new event when begin detected
            events.append({}) # Create the new event
            event_index += 1 # Increse index for each event
            field_empty = 0 # Used to count the empty fields
            events[event_index]["STATUS"] = 0 # STATUS is 0 if event is comming, 1 if event is happening, and 2 if event happened
            in_event = True # Used to know if the line is part of the event
            continue
        
        if not in_event : # Go next line if not in event
            continue
        
        if "END:VEVENT" in line : # Finalize event when end reached
            in_event = False
            continue
        #if "RRULE" in line :
            #if "UNTIL" in line:
                #if re.sub(".*UNTIL=+([^\s;]*);.*",r"\1",line) < timenow :
                    #continue
            #if "INTERVAL" in line:
                #interval = re.sub(".*INTERVAL=([0-9]*);.*",r"\1",line)
            #if "WEEKLY" in line:
                #week_day_start=datetime.strptime(events[event_index]["DTSTART"],'%Y%m%dT%H%M%SZ').isoweekday()
                #if timenow.isoweekday() == week_day_start:
                    
                #pass
            #elif "YEARLY" in line:
                #pass
            #elif "MONTHLY" in line:
                #pass
        if ("DTSTAMP" in line) or ("@" in line) or ("MODIFIED" in line) or ("TRANSP" in line) or ("CREAT" in line) or ("STATUS" in line) or ("SEQUENCE" in line) or ("APPLE" in line) : # Go next line if word detected, used to hide unwanted props
            continue
        
        if terms[1] == " " : # If attribute value is empty count it
            field_empty += 1
        
        if (field_empty > 1) or ( (events[event_index]["STATUS"] == 2) and exclude_passed) : # If too many filds are empty or if event passed, delete event
            events.pop()
            event_index -= 1
            field_empty = 0
            in_event = False
            continue
        
        if ("DTSTART" in line) or ("DTEND" in line):
            
            if ";" in line :
                terms[0] = line.split(";")[0]
            
            if len(terms[1]) > 10:
                if "Z" in terms[1]:
                    time_ = datetime.strptime(terms[1],"%Y%m%dT%H%M%SZ ") + timedelta(hours = 1)
                else:
                    time_ = datetime.strptime(terms[1],"%Y%m%dT%H%M%S ")
            else:
                time_ = datetime.strptime(terms[1],"%Y%m%d ")
            
            if weekly:
                week_day_event = time_.weekday()
                day_time_event = time_.time()
                difference = week_day_event-week_day_now
                time_ = datetime(datetime_now.year, datetime_now.month, datetime_now.day, time_.hour, time_.minute) + timedelta(days = difference)
            
            if time_ < datetime_now : # Compare time indicated with now
                events[event_index]["STATUS"] += 1
            terms[1] = time_
        
        events[event_index][terms[0]] = terms[1] # Append attribute to event
    return events

def sort_events(events, attribute="DTSTART"):
    ''' Sort event by attribute, default DTSTART'''
    return sorted(events, key = lambda i: i[attribute])

def get_calendar_sorted(index, exclude_passed = True, weekly = False):
    if isinstance(index,int):
        sorted_events = sort_events(get_event_from_text(index, exclude_passed, weekly))
    else:
        events = []
        for index_ in index:
            events += get_event_from_text(index_, exclude_passed, weekly)
        sorted_events = sort_events(events)
    return sorted_events

if __name__ == "__main__":
    print(get_calendar_sorted(3,True,True))
