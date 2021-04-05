#!/usr/bin/python3
import signal
import sys
from datetime import datetime
from display import Display
import system_commands
from os import system as os_system
import logging


logging.basicConfig(level=logging.WARNING)
cal_freeze = [200]
is_refreshing = False


def is_computer_on(host="kdaf"):
    response = os_system("ping -A -q -w 1 " + host + '> /dev/null')
    return (int(response) == 0)


def invert_display():
    str_time = str(datetime.now().time())
    is_sleep_time = not '05:30:00.000000' < str_time < '23:00:00.000000'
    is_night_time = not '08:00:00.000000' < str_time < '20:00:00.000000'
    if is_sleep_time or (is_night_time and not is_computer_on):
        return True
    else:
        return False


def time_refresh():
    if invert_display():
        return 1200
    else:
        return 180


def cleaning():  # Put here what to stop when program end
    EPDisplay.exit()


def refresh_screen(refresh_time=0):
    global is_refreshing
    if is_refreshing:
        return
    is_refreshing = True
    EPDisplay.invert = invert_display()
    EPDisplay.minimal = EPDisplay.invert
    system_commands.set_pwr_led(1)

    logging.info(f"\nRefresh{datetime.now()}")
    system_commands.set_pwr_led(0)
    if refresh_time != 0:
        EPDisplay.interval = refresh_time
    EPDisplay.refresh()
    is_refreshing = False


def Interruption(sig, frame):
    print("\n\nSIGINT received")
    cleaning()
    sys.exit(0)


def User1(sig, frame):
    print("\n\nSIGUSR1 received")
    refresh_screen()


try:
    signal.signal(signal.SIGINT, Interruption)
    signal.signal(signal.SIGUSR1, User1)

    from time import sleep as time_sleep

    logging.info("Program starts")
    EPDisplay = Display()
    system_commands.set_pwr_led(0)
    while True:
        refresh_time = time_refresh()
        refresh_screen(refresh_time)
        logging.info(f"Refresh every {refresh_time} sec")
        minutes_to_sleep = (3600-datetime.now().minute*60) % refresh_time
        if minutes_to_sleep == 0:
            minutes_to_sleep = refresh_time
        time_to_sleep = minutes_to_sleep - datetime.now().second
        time_sleep(time_to_sleep)

except Exception as e:
    print(e)
    print("\nError")
    cleaning()
