#!/usr/bin/python3
from os import system as execute_shell
from subprocess import check_output
import logging


class Music_lib():
    def __init__(self):
        self.is_mocp_on = False

    def is_mocp(self):
        if not self.is_mocp_on:
            pid = int(check_output(['pgrep', 'mocp']).decode('utf-8').splitlines()[0])
            self.is_mocp_on = pid != 256
            return pid != 256
        else:
            return True

    def get_status_mocp(self):
        if self.is_mocp():
            infos = check_output(['mocp', '-i']).decode('utf-8').splitlines()[:-1]
            infos_dict = {}
            for info in infos:
                info = info.split(": ")
                infos_dict[info[0]] = info[1]
            return infos_dict
        else:
            return {}

    def start_mocp(self):
        if not self.is_mocp():
            print('Turning mocp on')
            execute_shell('mocp --server')
            # If it wont start, raise problem
            if not self.is_mocp():
                logging.info("Mocp wont start")
                raise Exception("Mocp not started")

    def play_mocp(self):
        self.start_mocp()
        execute_shell('mocp --play')

    def toggle_pause_mocp(self):
        if self.is_mocp():
            execute_shell('mocp --toggle-pause')

    def next_track_mocp(self):
        if self.is_mocp():
            execute_shell('mocp --next')

    def previous_track_mocp(self):
        if self.is_mocp():
            execute_shell('mocp --previous')

    def stop_mocp(self):
        if self.is_mocp():
            execute_shell('mocp --stop')

    def exit_mocp(self):
        if self.is_mocp():
            execute_shell('mocp --exit')
            self.is_mocp_on = False

    def queue_add_mocp(self, file_path):
        if self.is_mocp():
            execute_shell(f'mocp --append {file_path}')

    def queue_clear_mocp(self):
        if self.is_mocp():
            execute_shell('mocp --clear')


if __name__ == "__main__":
    music = Music_lib()
    music.toggle_pause_mocp()
