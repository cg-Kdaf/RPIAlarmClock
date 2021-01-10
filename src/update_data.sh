#!/bin/sh

# Get the calendars
index=0

while IFS= read -r line; do
    wget -q ${line} -O "/home/pi/AlarmClockProject/AlarmClock/cache/calendars/calendar${index}.ics"
    index=$((index+1))
done < /home/pi/AlarmClockProject/AlarmClock/data/calendars.txt

# Get the weather

index=0

while IFS= read -r line; do
    wget -q ${line} -O "/home/pi/AlarmClockProject/AlarmClock/cache/weathers/weather${index}.json"
    index=$((index+1))
done < /home/pi/AlarmClockProject/AlarmClock/data/weathers.txt
