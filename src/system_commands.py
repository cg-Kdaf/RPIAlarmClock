#!/usr/bin/python3
from os import system as execute_shell
from subprocess import run,check_output
from time import sleep as time_sleep


def set_pwr_led(status):
    """Brightness between 0 and 1"""
    execute_shell(f'echo {status} | sudo tee /sys/class/leds/led0/brightness >/dev/null')

def stop_alarm():
    execute_shell("/home/pi/AlarmClockProject/AlarmClock/auto_scripts/stop.sh")
    time_sleep(4)

def start_alarm():
    execute_shell("/home/pi/AlarmClockProject/AlarmClock/auto_scripts/start.sh")

def restart_alarm():
    stop_alarm()
    start_alarm()

def power_off():
    stop_alarm
    execute_shell("sudo poweroff")

def refresh_data_cached():
    execute_shell("/home/pi/AlarmClockProject/AlarmClock/src/update_data.sh")

def start_programm_at(program, date_time):
    """Return process id (start at 1)
    arg1 if program name (str) ex : /bin/sh
    arg2 is time of execution (datetime obj)
    """
    output_ = check_output(program+" | at " + date_time.strftime('%H:%M %B %d'))
    output_ = check_output("echo " + output_.split('\n')[1] + " | sed -s 's/.*job\ \([0-9]*\).*/\1/p'")
    return output_

def list_program_at():
    """Return list of indexes of running prog at"""
    processes = check_output(["at", "-l"]).decode('utf-8').split("\n")[:-1]
    processes = [''.join([i for i in process[0:4].replace(" ","") if i.isdigit()]) for process in processes]
    return processes

def remove_program_at(index):
    execute_shell(f"atrm {index}")
