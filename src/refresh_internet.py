import socket
from time import sleep as time_sleep
import system_commands
from datetime import datetime

from calendars import get_calendar_sorted

refresh_offline = 6
refresh_online = 15
alarm_activated = True  # This is for knowing when to delete the alarms: only first time if is off
ring_program = "python3 /home/pi/AlarmClockProject/AlarmClock/src/sound.py"


def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


def refresh_alarms():
    global alarm_activated
    activated = open("/home/pi/AlarmClockProject/AlarmClock/cache/alarm_status", "r").read()

    alarms_infos_by_alarm = system_commands.list_program_at()
    for index, alarm in enumerate(alarms_infos_by_alarm):
        time_start = datetime.strptime(f"{alarm[1]} {alarm[2]} {alarm[3]} {alarm[4]} {alarm[5]}",
                                       "%a %b %d %H:%M:%S %Y")
        alarms_infos_by_alarm[index] = [alarm[0], time_start]

    alarms_infos = []
    if alarms_infos_by_alarm != []:
        for list_column in range(len(alarms_infos_by_alarm[0])):  # For each element of the alarms
            alarms_infos.append([])
            for row in range(len(alarms_infos_by_alarm)):  # For each alarm
                alarms_infos[list_column].append(alarms_infos_by_alarm[row][list_column])
        alarms_id = [int(alarm_infos) for alarm_infos in alarms_infos[0]]

    alarms = get_calendar_sorted(3, True, True)

    if "0" in activated and alarm_activated:
        # Remove alarms planned if Alarms are diactivated
        if alarms_infos_by_alarm != []:
            print("Will remove alarms with id:")
            for alarm_id in alarms_id:
                print(alarm_id)
                system_commands.remove_program_at(int(alarm_id))
        alarm_activated = False

    used_alarms = []
    if "1" in activated:
        if alarms == []:
            return
        for alarm in alarms:
            if alarm["STATUS"] == 1:
                continue
            time_start = alarm["DTSTART"]
            if alarms_infos_by_alarm != []:
                if time_start in alarms_infos[1]:
                    used_alarms.append(alarms_infos[0][alarms_infos[1].index(time_start)])
                    continue
            print("Add alarm")
            time_start_str = time_start.strftime('%H:%M %B %d')
            new_alarm_id = system_commands.start_programm_at(ring_program, time_start_str, True)
            used_alarms.append(new_alarm_id)
        alarm_activated = True
    alarms_to_remove = list(set(alarms_infos[0]) - set(used_alarms))
    if alarms_to_remove != []:
        for alarm_id in alarms_to_remove:
            print(f"Alarm {alarm_id} will be removed")
            system_commands.remove_program_at(int(alarm_id))


while True:
    if not internet():
        time_to_sleep = refresh_offline*60
        print("NO INTERNET")
    else:
        print("INTERNET CONNECTED")
        print("refreshing data")
        # system_commands.refresh_data_cached()
        time_to_sleep = refresh_online*60
    print("refreshing alarms")
    refresh_alarms()
    print("sleep")
    time_sleep(time_to_sleep)
