#!/bin/sh 

sudo systemctl kill AlarmClock.service --signal=SIGINT
sudo systemctl kill Utilities_PWR.service --signal=SIGINT
