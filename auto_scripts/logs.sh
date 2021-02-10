#!/bin/sh 

journalctl -b -u AlarmClock.service --lines=30 -q | cut --complement -d' ' -f4-5
echo "\n\nPWR Programm\n\n"
journalctl -b -u Utilities_PWR.service --lines=30 -q | cut --complement -d' ' -f4-5

