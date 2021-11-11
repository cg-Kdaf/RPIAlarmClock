#!/usr/bin/python3
from os import system as execute_shell
from subprocess import check_output
from time import sleep as time_sleep
from datetime import datetime


def set_pwr_led(status):
    """Brightness between 0 and 1"""
    execute_shell(f'echo {status} | sudo tee /sys/class/leds/led0/brightness > /dev/null 2>&1')


def stop_alarm():
    execute_shell("/home/pi/AlarmClockProject/AlarmClock/auto_scripts/stop.sh")
    time_sleep(4)


def start_alarm():
    execute_shell("/home/pi/AlarmClockProject/AlarmClock/auto_scripts/start.sh")


def restart_alarm():
    stop_alarm()
    start_alarm()


def power_off():
    stop_alarm()
    execute_shell("sudo poweroff")


def refresh_data_cached():
    execute_shell("/home/pi/AlarmClockProject/AlarmClock/src/update_data.sh")


def start_programm_at(program, time_, return_id=False):
    """Return process id (start at 1)
    arg1 if program name (str) ex : /bin/sh
    arg2 is time of execution time undertandable by at (str)
    """
    if return_id:
        programs_before = list_program_at(True)
    execute_shell('echo "' + program+'" | at ' + time_)
    if return_id:
        programs_after = list_program_at(True)
        print(programs_before, programs_after)
        if programs_before != [] and programs_before != []:
            created = list(set(programs_after) - set(programs_before))[0]
        else:
            created = programs_after[0]
        print(created)
        return created


def list_program_at(id_only=False):
    """Return list of indexes of running prog at
    example of elt : ['193', 'Wed', 'Oct', '6', '06:15:00', '2021', 'a', 'pi', time]
    """
    processes = check_output(["atq"]).decode('utf-8').split("\n")[:-1]
    processes = [process.replace("\t", " ").replace("  ", " ").split(" ") for process in processes]
    if 1:  # Sort them
        for process in processes:
            date = datetime.strptime("".join(process[1:6]), "%a%b%d%H:%M:%S%Y")
            process.append(date)
        processes.sort(key=(lambda process: process[-1]))
    if id_only:
        processes = [process[0] for process in processes]
    return processes


def remove_program_at(index):
    execute_shell(f"atrm {index}")


def send_signal(process_name, signal):
    """ Send signal(str) to the process(str) with correspondence to full command """
    execute_shell(f'pkill -f "{process_name}" --signal {signal}')
