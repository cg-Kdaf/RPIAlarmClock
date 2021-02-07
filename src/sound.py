#!/usr/bin/python3
import RPi.GPIO as GPIO
from time import sleep as time_sleep
from music_commands import Music_lib

def ring():
    speaker_pin = 13 # GPIO Pin
    dutycycle = 10
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(speaker_pin,GPIO.OUT)
    __buzzer = GPIO.PWM(speaker_pin, 1000) # Set frequency to 1000hz (initial value, change to something else afterward)
    __buzzer.start(dutycycle)
    for i in range(10):
        __buzzer.ChangeFrequency(440)
        time_sleep(.3)
        __buzzer.ChangeFrequency(600)
        time_sleep(.3)
    __buzzer.stop()
    GPIO.cleanup()


if __name__ == "__main__":
    mocp = Music_lib()
    mocp.play_mocp()
    # ring()
