#!/usr/bin/python3
import signal
import sys
from time import time as time_time, sleep as time_sleep
import RPi.GPIO as GPIO

"""
This file is separated from others, to evoid errors.
If the main.py get an error, this script will not stop,
    so I'll be able to turnoff RPi without having to disconect cable or doing it via ssh
"""


BUTTON_GPIO1 = 22
is_triggered = False
start = None


def signal_handler(sig, frame):
    print("Exiting")
    GPIO.cleanup()
    sys.exit(0)


def button1_callback(channel):
    global is_triggered, start
    if not GPIO.input(BUTTON_GPIO1):
        start = time_time()
        test = start
        time_sleep(.2)
        if test == start:
            print("accounting")


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(BUTTON_GPIO1, GPIO.BOTH, callback=button1_callback)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
