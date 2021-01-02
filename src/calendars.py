#!/usr/bin/python3
from requests import get as requests_get
from arrow import now as arrow_now,get as arrow_get
#from datetime import datetime
#import re

calendars = [
    "https://api.ecoledirecte.com/v3/ical/E/6940/516d313257576c78646d45726348704d4e6e427a566e4656547a427459335a334d6974694d557052.ics",# School
    "https://calendar.google.com/calendar/ical/kdblender%40gmail.com/private-85da5612bb050accd256813f2f9778ef/basic.ics", # KDblender
    "https://calendar.google.com/calendar/ical/e4lqs9coricqs6h5h8ke5pmglc%40group.calendar.google.com/private-20f21485608b613726a760b2b682c49a/basic.ics" # Family
    "https://calendar.google.com/calendar/ical/ndo2c5pl0b5hnsdcoqqvm3ptcs%40group.calendar.google.com/private-4041c4e7335061c24806c5950ff87758/basic.ics" # Alarm Clock
]

def get_calendar(url):
    return requests_get(url).text

def get_event_from_text(text_file,exclude_passed = True):
    '''Get events upcomming from a ics textfile'''
    timenow = arrow_now().format("YYYYMMDDTHHmmss")+"Z"
    events=[]
    in_event = False
    field_empty = 0
    event_index = -1
    
    for line in text_file.splitlines():
        
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
        if ("DTSTAMP" in line) or ("UID" in line) or ("@" in line) or ("MODIFIED" in line) or ("TRANSP" in line) or ("CREAT" in line) or ("STATUS" in line) or ("SEQUENCE" in line) or ("APPLE" in line) : # Go next line if word detected, used to hide unwanted props
            continue
        
        if terms[1] == " " : # If attribute value is empty count it
            field_empty += 1
        
        if (field_empty > 1) or ( (events[event_index]["STATUS"] == 2) and exclude_passed) : # If too many filds are empty or if event passed, delete event
            events.pop()
            event_index -= 1
            field_empty = 0
            in_event = False
            continue
        
        if ("DTSTART" in line) or ("DTEND" in line) :
            if ";" in line :
                terms[0] = line.split(";")[0]
            if terms[1] < timenow : # Compare time indicated with now
                events[event_index]["STATUS"] += 1
        
        events[event_index][terms[0]] = terms[1] # Append attribute to event
    
    return events

def sort_events(events, attribute="DTSTART"):
    ''' Sort event by attribute, default DTSTART'''
    return sorted(events, key = lambda i: i[attribute])

def get_calendar_sorted(url):
    return sort_events(get_event_from_text(get_calendar(url)))

def get_calendars_sorted(urls):
    events = []
    for url in urls:
        events += get_event_from_text(get_calendar(url))
    return sort_events(events)
