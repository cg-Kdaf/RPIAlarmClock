#!/bin/sh 

lines=30

if [ $# != "0" ]
then
    lines=${1}
fi

journalctl -b -u AlarmClock.service --lines=${lines} -q | cut --complement -d' ' -f4-5
echo "\n\nPWR Programm\n\n"
journalctl -b -u Utilities_PWR.service --lines=${lines} -q | cut --complement -d' ' -f4-5
echo "\n\nCrontab\n\n"
grep --ignore-case CRON /var/log/syslog | tail -${lines} | grep -v 'hourly' | grep -v 'weekly' | grep -v 'daily'
