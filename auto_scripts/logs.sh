#!/bin/sh 

journalctl -b -u AlarmClock.service --lines=30 --output=cat
echo "\n\nPWR Programm\n\n"
journalctl -b -u Utilities_PWR.service --lines=30 --output=cat

