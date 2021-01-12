#!/usr/bin/python3
from os import system as execute_shell
from time import sleep as time_sleep

def set_pwr_led(status):
    """Brightness between 0 and 1"""
    execute_shell(f'echo {status} | sudo tee /sys/class/leds/led0/brightness >/dev/null')

def stop_alarm():
    execute_shell("/home/pi/AlarmClockProject/AlarmClock/auto_scripts/stop.sh")
    time_sleep(4)

def start_alarm():
    execute_shell("/home/pi/AlarmClockProject/AlarmClock/auto_scripts/start.sh")

def restart_alarm():
    stop_alarm()
    start_alarm()

def power_off():
    stop_alarm
    execute_shell("sudo poweroff")

def refresh_data_cached():
    execute_shell("/home/pi/AlarmClockProject/AlarmClock/src/get_calendars.sh")
