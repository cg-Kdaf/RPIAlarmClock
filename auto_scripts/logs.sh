#/bin/sh 

journalctl -b -u AlarmClock.service --lines=30 --output=cat

