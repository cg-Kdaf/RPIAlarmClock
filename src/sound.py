#!/usr/bin/python3
# import RPi.GPIO as GPIO
from time import sleep as time_sleep
from music_commands import Music_lib
from os import listdir


# def ring():
#     speaker_pin = 13  # GPIO Pin
#     dutycycle = 10
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(speaker_pin, GPIO.OUT)
#     __buzzer = GPIO.PWM(speaker_pin, 1000)  # Set frequency to 1000hz (initial value, change to something else afterward)
#     __buzzer.start(dutycycle)
#     for i in range(10):
#         __buzzer.ChangeFrequency(440)
#         time_sleep(.3)
#         __buzzer.ChangeFrequency(600)
#         time_sleep(.3)
#     __buzzer.stop()
#     GPIO.cleanup()


def mocp_play():
    mocp = Music_lib()
    mocp.queue_clear_mocp()
    playlists = listdir('/home/pi/Music/')
    first_playlist = [p_name for p_name in playlists if "First" in p_name]
    first_music = listdir(f"/home/pi/Music/{first_playlist[0]}/")[0]
    first_music_path = f"/home/pi/Music/{first_playlist[0]}/{first_music}"
    mocp.queue_add_mocp(f'"{first_music_path}"')
    playlists.pop(playlists.index(first_playlist[0]))
    for playlist in playlists:
        mocp.queue_add_mocp(f'"/home/pi/Music/{playlist}"')
    mocp.play_mocp()


if __name__ == "__main__":
    mocp_play()
    # ring()
