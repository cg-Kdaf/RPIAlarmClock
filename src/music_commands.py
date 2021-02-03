#!/usr/bin/python3
from os import system as execute_shell
from os import system as os_system
import logging


class Music_lib():
    def __init__(self):
        pass

    def is_mocp(self):
        pid = os_system('pgrep mocp')
        return pid != 256

    def start_mocp(self):
        if not self.is_mocp():
            print('Turning mocp on')
            execute_shell('mocp -S')
            # If it wont start, raise problem
            if not self.is_mocp():
                logging.info("Mocp wont start")
                raise Exception("Mocp not started")

    def play_mocp(self):
        self.start_mocp()
        execute_shell('mocp -p')

    def toggle_pause_mocp(self):
        if self.is_mocp():
            execute_shell('mocp -G')

    def next_track_mocp(self):
        if self.is_mocp():
            execute_shell('mocp -f')

    def previous_track_mocp(self):
        if self.is_mocp():
            execute_shell('mocp -r')

    def stop_mocp(self):
        if self.is_mocp():
            execute_shell('mocp -s')

    def exit_mocp(self):
        if self.is_mocp():
            execute_shell('mocp -x')


if __name__ == "__main__":
    music = Music_lib()
    music.toggle_pause_mocp()
