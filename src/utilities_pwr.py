#!/usr/bin/python3
import signal
import sys
from time import time as time_time, sleep as time_sleep
import RPi.GPIO as GPIO
from system_commands import set_pwr_led, power_off, send_signal, execute_shell
from music_commands import Music_lib
from refresh_internet import refresh_alarms, refresh_internet

"""
This file is separated from others, to evoid errors.
If the main.py get an error, this script will not stop,
    so I'll be able to turnoff RPi without having to disconect cable or doing it via ssh
    Buttons are connected to the pins given in BUTTON_GPIOx and they are connected on the other side to the 3.3V via a resistor of 10KOhms
"""

BUTTON_GPIO1 = 26
BUTTON_GPIO2 = 13
music = Music_lib()

def button_callback(channel, press_duration):
    print(press_duration, channel)
    if channel == BUTTON_GPIO1:
        if 5 < press_duration < 10:  # Long press for shutdown
            print("Turning off")
            for i in range(30):
                set_pwr_led(0)
                time_sleep(1/(i+2))
                set_pwr_led(1)
                time_sleep(1/(i+2))
                if not GPIO.input(BUTTON_GPIO1):
                    print("Abort poweroff")
                    set_pwr_led(0)
                    return
            time_sleep(2)
            power_off()
        elif 0.1 < press_duration < 1.5:   # Short press for "instant" refresh
            print("Sending SIGUSR1 to main.py")
            send_signal("main.py", "SIGUSR1")
        elif 1.5 < press_duration < 5:   # Medium press for data refresh
            print("Refreshing cached datas")
            refresh_internet()
    elif channel == BUTTON_GPIO2:
        if 2 < press_duration < 5:   # Medium press for alarm toggling
            activated = open("/home/pi/AlarmClockProject/AlarmClock/cache/alarm_status", "r").read()
            if "1" in activated:
                execute_shell("echo 0 > /home/pi/AlarmClockProject/AlarmClock/cache/alarm_status")
                print("Set alarm to off")
            else:
                execute_shell("echo 1 > /home/pi/AlarmClockProject/AlarmClock/cache/alarm_status")
                print("Set alarm to on")
            print("Refresh alarm and display")
            refresh_alarms()
            send_signal("main.py", "SIGUSR1")
        elif 0.1 < press_duration < 1:   # Short press for pause mocp
            print("Music playpause")
            music.toggle_pause_mocp()
            set_pwr_led(1)
            time_sleep(.2)
            set_pwr_led(0)
            time_sleep(.2)
            set_pwr_led(1)
            time_sleep(.5)
            set_pwr_led(0)
        elif 7 < press_duration < 10:   # Medium press for exiting mocp
            print("Music exit")
            music.exit_mocp()
            set_pwr_led(1)
            time_sleep(2)
            set_pwr_led(0)


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTON_GPIO2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    try:
        while True:
            time_sleep(.05)

            if GPIO.input(BUTTON_GPIO1):
                time_start = time_time()
                time_sleep(.05)
                if not GPIO.input(BUTTON_GPIO1):
                    continue
                while True:
                    time_sleep(.05)
                    if not GPIO.input(BUTTON_GPIO1):
                        button_callback(BUTTON_GPIO1, time_time() - time_start)
                        break

            if GPIO.input(BUTTON_GPIO2):
                time_start = time_time()
                time_sleep(.05)
                if not GPIO.input(BUTTON_GPIO2):
                    continue
                while True:
                    time_sleep(.05)
                    if not GPIO.input(BUTTON_GPIO2):
                        button_callback(BUTTON_GPIO2, time_time() - time_start)
                        break
    except KeyboardInterrupt:
        print("Exiting")
        GPIO.cleanup()
        sys.exit(0)
