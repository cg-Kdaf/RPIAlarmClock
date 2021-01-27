#!/usr/bin/python3
import logging
import signal
import sys
from datetime import datetime
from display import Display
import system_commands

logging.basicConfig(level=logging.DEBUG)


def cleaning():  # Put here what to stop when program end
    EPDisplay.exit()


def refresh_screen():
    system_commands.set_pwr_led(1)

    print("\nRefresh", datetime.now())
    system_commands.set_pwr_led(0)
    EPDisplay.refresh()


def Interruption(sig, frame):
    print("\n\nSIGINT received")
    cleaning()
    sys.exit(0)


def User1(sig, frame):
    print("SIGUSR1 received")
    refresh_screen()


try:
    signal.signal(signal.SIGINT, Interruption)
    signal.signal(signal.SIGUSR1, User1)

    from time import time as time_time, sleep as time_sleep
    starttime = time_time()

    print("Program starts")
    EPDisplay = Display()
    system_commands.set_pwr_led(0)
    while True:

        if '06:00:00.000000' < str(datetime.now().time()) < '20:00:00.000000':
            EPDisplay.invert = False
            refresh_time = 180
        else:   # If night do invert the screen, to see from the bed AND set refresh time to 1200sec
            refresh_time = 1200
            EPDisplay.invert = True

        refresh_screen()
        print("Refresh every ", refresh_time, "sec")
        time_to_sleep = refresh_time - ((time_time() - starttime) % refresh_time)
        time_sleep(time_to_sleep)

except Exception:
    print("\nError")
    cleaning()
