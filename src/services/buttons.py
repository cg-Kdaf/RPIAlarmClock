#!/usr/bin/python3
import signal                   
import sys
from time import time as time_time
import RPi.GPIO as GPIO

BUTTON_GPIO = 26
press_start = None

def signal_handler(sig, frame):
    print("Exiting")
    GPIO.cleanup()
    sys.exit(0)

def button_callback(channel):
    global press_start
    if not GPIO.input(BUTTON_GPIO):
        print("Button pressed!")
        press_start = time_time()
    else:
        print("Button released!")
        press_duration = time_time() - press_start
        
        if 5 < press_duration < 10 :
            print("Turning off")
        

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.BOTH, 
            callback=button_callback, bouncetime=100)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
