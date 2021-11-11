#!/usr/bin/python3
# import RPi.GPIO as GPIO
from music_commands import Music_lib
from os import listdir
from system_commands import send_signal


def mocp_play():
    send_signal("main.py", "SIGUSR1")
    mocp = Music_lib()
    mocp.queue_clear_mocp()
    playlists = listdir('/home/pi/Music/')
    first_playlist = [p_name for p_name in playlists if "First" in p_name]
    first_music = None
    for file in listdir(f"/home/pi/Music/{first_playlist[0]}/"):
        if ".lrc" in file:
            continue
        first_music = file
        break
    print(first_music)
    first_music_path = f"/home/pi/Music/{first_playlist[0]}/{first_music}"
    mocp.queue_add_mocp(f'"{first_music_path}"')
    playlists.pop(playlists.index(first_playlist[0]))
    for playlist in playlists:
        mocp.queue_add_mocp(f'"/home/pi/Music/{playlist}"')
    mocp.play_mocp()


if __name__ == "__main__":
    mocp_play()
