from calendars import get_calendar_sorted
from time import sleep as time_sleep
from datetime import datetime
from sound import speaker

speaker = speaker()


while True:
    alarms = get_calendar_sorted(3, True, True)
    if alarms == []:
        break
    upcomming = {}
    for alarm in alarms:
        if alarm["STATUS"] == 0:
            upcomming = alarm
            break
    time_to_delay = upcomming["DTSTART"] - datetime.now()
    print(time_to_delay.total_seconds())
    time_sleep(time_to_delay.total_seconds())
    #time_sleep(5)
    speaker.ring()
    break
