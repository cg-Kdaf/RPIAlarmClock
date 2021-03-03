#!/bin/sh

# Get the calendars
echo 'Get calendar'
index=0

while IFS= read -r line; do
    wget -q ${line} -O "/home/pi/AlarmClockProject/AlarmClock/cache/calendars/calendar${index}.ics"
    index=$((index+1))
done < /home/pi/AlarmClockProject/AlarmClock/data/calendars.txt

# Get the weather
echo 'Get weather data'

index=0

while IFS= read -r line; do
    wget -q ${line} -O "/home/pi/AlarmClockProject/AlarmClock/cache/weathers/weather${index}.json"
    index=$((index+1))
done < /home/pi/AlarmClockProject/AlarmClock/data/weathers.txt

# Get the tasks
echo 'Get tasks'

python3 /home/pi/AlarmClockProject/AlarmClock/src/google_tasks.py

# Get the ecoledirect data
echo 'Get ED datas'

python3 /home/pi/AlarmClockProject/AlarmClock/src/ED_utilities.py

# Get the deezer datas
echo 'Get deezer musics'

python3 /home/pi/AlarmClockProject/AlarmClock/src/deezer_musics.py
