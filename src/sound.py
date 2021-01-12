#!/usr/bin/python3
import RPi.GPIO as GPIO
from time import sleep as time_sleep


class speaker:
    

    def __init__(self, volume = 1.):
        self.speaker_pin = 13 # GPIO Pin
        self.dutycycle = 10
        self.volume = volume
        
    
    def ring(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.speaker_pin,GPIO.OUT)
        self.__buzzer = GPIO.PWM(self.speaker_pin, 1000) # Set frequency to 1000hz (initial value, change to something else afterward)
        self.__buzzer.start(self.dutycycle)
        for i in range(10):
            self.__buzzer.ChangeFrequency(440)
            time_sleep(.3)
            self.__buzzer.ChangeFrequency(600)
            time_sleep(.3)
        self.__buzzer.stop()
        GPIO.cleanup()

#speaker = speaker()
#speaker.ring()
#speaker.clean_gpio()
