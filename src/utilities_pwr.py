#!/usr/bin/python3
import signal
import sys
from time import time as time_time, sleep as time_sleep
import RPi.GPIO as GPIO
from system_commands import set_pwr_led, power_off, send_signal, execute_shell, refresh_data_cached
from music_commands import Music_lib
import refresh_internet

"""
This file is separated from others, to evoid errors.
If the main.py get an error, this script will not stop,
    so I'll be able to turnoff RPi without having to disconect cable or doing it via ssh
"""


BUTTON_GPIO1 = 26
BUTTON_GPIO2 = 19
press_start1 = None
pressing1 = False
press_start2 = None
pressing2 = False
music = Music_lib()


def signal_handler(sig, frame):
    print("Exiting")
    GPIO.cleanup()
    sys.exit(0)


def button1_callback(channel):
    global press_start1, pressing1
    if GPIO.input(BUTTON_GPIO1):
        time_sleep(.05)
        if not GPIO.input(BUTTON_GPIO1) or not pressing1:
            return
        pressing1 = False

        press_duration = time_time() - press_start1
        if 5 < press_duration < 10:  # Long press for shutdown
            print("Turning off")
            for i in range(30):
                set_pwr_led(0)
                time_sleep(1/(i+2))
                set_pwr_led(1)
                time_sleep(1/(i+2))
                if not GPIO.input(BUTTON_GPIO1):
                    print("Abort poweroff")
                    return
            time_sleep(2)
            power_off()
        elif 0.1 < press_duration < 1.5:   # Short press for "instant" refresh
            print("Sending SIGUSR1 to main.py")
            send_signal("main.py", "SIGUSR1")
        elif 1.5 < press_duration < 5:   # Medium press for data refresh
            print("Refreshing cached datas")
            refresh_data_cached()

    else:
        time_sleep(.05)
        if GPIO.input(BUTTON_GPIO1) or pressing1:
            return
        press_start1 = time_time()
        pressing1 = True


def button2_callback(channel):
    global press_start2, pressing2, music
    if GPIO.input(BUTTON_GPIO2):
        time_sleep(.05)
        if not GPIO.input(BUTTON_GPIO2) or not pressing2:
            return
        pressing2 = False

        press_duration = time_time() - press_start2
        if 2 < press_duration < 5:
            print("Test")
            activated = open("/home/pi/AlarmClockProject/AlarmClock/cache/alarm_status", "r").read()
            if "1" in activated:
                execute_shell("echo 0 > /home/pi/AlarmClockProject/AlarmClock/cache/alarm_status")
                print("Set alarm to off")
            else:
                execute_shell("echo 1 > /home/pi/AlarmClockProject/AlarmClock/cache/alarm_status")
                print("Set alarm to on")
            print("Refresh alarm and display")
            send_signal("main.py", "SIGUSR1")
            refresh_internet.refresh_alarms()
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
    else:
        time_sleep(.05)
        if GPIO.input(BUTTON_GPIO2) or pressing2:
            return
        press_start2 = time_time()
        pressing2 = True


if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_GPIO2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(BUTTON_GPIO1, GPIO.BOTH, callback=button1_callback)
    GPIO.add_event_detect(BUTTON_GPIO2, GPIO.BOTH, callback=button2_callback)

    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
