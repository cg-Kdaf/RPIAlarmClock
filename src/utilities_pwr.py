#!/usr/bin/python3
import signal
import sys
from time import time as time_time, sleep as time_sleep
import RPi.GPIO as GPIO
from system_commands import set_pwr_led, power_off, send_signal

"""
This file is separated from others, to evoid errors.
If the main.py get an error, this script will not stop,
    so I'll be able to turnoff RPi without having to disconect cable or doing it via ssh
"""


BUTTON_GPIO = 26
press_start = None
pressing = False

def signal_handler(sig, frame):
    print("Exiting")
    GPIO.cleanup()
    sys.exit(0)

def button_callback(channel):
    global press_start, pressing
    if GPIO.input(BUTTON_GPIO):
        time_sleep(.05)
        if not GPIO.input(BUTTON_GPIO) or not pressing:
            return
        pressing = False
        
        press_duration = time_time() - press_start
        if 3 < press_duration < 15 : # Long press for shutdown
            print("Turning off")
            for i in range(30):
                set_pwr_led(0)
                time_sleep(1/(i+2))
                set_pwr_led(1)
                time_sleep(1/(i+2))
                if not GPIO.input(BUTTON_GPIO):
                    print("Abort poweroff")
                    return
            time_sleep(2)
            power_off()
        elif 0.1 < press_duration < 1 : # Short press for "instant" refresh
            print("Sending SIGUSR1 to main.py")
            send_signal("main.py","SIGUSR1")
    else:
        time_sleep(.05)
        if GPIO.input(BUTTON_GPIO) or pressing:
            return
        press_start = time_time()
        pressing = True

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.BOTH, callback=button_callback)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
