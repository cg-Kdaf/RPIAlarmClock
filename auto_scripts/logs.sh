#/bin/sh 

journalctl -b -u AlarmClock.service --lines=200 --output=cat

