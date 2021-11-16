#!/usr/bin/python3
# import RPi.GPIO as GPIO
from music_commands import Music_lib
from os import listdir
from system_commands import send_signal
from random import shuffle


def mocp_play():
    send_signal("main.py", "SIGUSR1")
    mocp = Music_lib()
    mocp.queue_clear_mocp()
    playlists = [dir for dir in listdir('/home/pi/Music/') if "." not in dir]
    first_playlist = [p_name for p_name in playlists if "First" in p_name]
    first_music = None
    for file in listdir(f"/home/pi/Music/{first_playlist[0]}/"):
        if ".mp3" in file:
            first_music = file
            break
    print(first_music)
    first_music_path = f"/home/pi/Music/{first_playlist[0]}/{first_music}"
    mocp.queue_add_mocp(f'"{first_music_path}"')
    playlists.pop(playlists.index(first_playlist[0]))
    print(playlists)
    for playlist in playlists:
        music_files = listdir(f"/home/pi/Music/{playlist}/")
        shuffle(music_files)
        for music_file in music_files:
            if ".mp3" in music_file:
                music_file = music_file.replace(" ", "\ ")
                print(music_file)
                mocp.queue_add_mocp(f"/home/pi/Music/{playlist}/{music_file}")
    mocp.play_mocp()


if __name__ == "__main__":
    mocp_play()
