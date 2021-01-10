#!/bin/sh

# for url in ${urls}
# do
# wget --directory-prefix='/home/pi/AlarmClockProject/AlarmClock/cache/' ${url}
# done

index=0

while IFS= read -r line; do
    wget ${line} -O "/home/pi/AlarmClockProject/AlarmClock/cache/calendar${index}.ics"
    index=${index}+1
done < /home/pi/AlarmClockProject/AlarmClock/data/calendars.txt
