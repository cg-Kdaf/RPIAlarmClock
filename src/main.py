#!/usr/bin/python3
import signal
import sys
from datetime import datetime
from display import Display
import system_commands
from os import system as os_system
import logging


logging.basicConfig(level=logging.WARNING)
cal_freeze = [0]
is_refreshing = False


def is_computer_on(host="kdaf"):
    response = os_system("ping -A -q -w 1 " + host + '> /dev/null')
    return (int(response) == 0)


def invert_display():
    computer = is_computer_on()
    day = '06:00:00.000000' < str(datetime.now().time()) < '20:00:00.000000'
    if computer or day:
        return False
    else:
        return True


def time_refresh():
    in_event_freeze = any(event['CAL_ID'] in cal_freeze for event in EPDisplay.happening_events)
    if in_event_freeze:
        return 3600
    elif '06:00:00.000000' < str(datetime.now().time()) < '20:00:00.000000':
        return 180
    else:
        return 1200


def cleaning():  # Put here what to stop when program end
    EPDisplay.exit()


def refresh_screen():
    global is_refreshing
    if is_refreshing:
        return
    is_refreshing = True
    EPDisplay.invert = invert_display()
    system_commands.set_pwr_led(1)

    logging.info(f"\nRefresh{datetime.now()}")
    system_commands.set_pwr_led(0)
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

    from time import time as time_time, sleep as time_sleep
    starttime = time_time()

    logging.info("Program starts")
    EPDisplay = Display()
    system_commands.set_pwr_led(0)
    while True:
        refresh_screen()
        refresh_time = time_refresh()
        logging.info(f"Refresh every {refresh_time} sec")
        time_to_sleep = refresh_time - ((time_time() - starttime) % refresh_time)
        time_sleep(time_to_sleep)

except Exception as e:
    print(e)
    print("\nError")
    cleaning()
