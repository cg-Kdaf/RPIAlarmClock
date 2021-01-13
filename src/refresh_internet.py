import socket
from time import sleep as time_sleep
import system_commands

refresh_offline = 6
refresh_online = 15
alarms = []

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
    activated = open("/home/pi/AlarmClockProject/AlarmClock/cache/alarm_status","r").read()
    if "0" in activated:
        alarms_id = system_commands.list_program_at()
        if alarms_id != []:
            print("Will remove alarms with id:"+str(alarms_id))
            for alarm_id in alarms_id:
                system_commands.remove_program_at(alarm_id)
    else:
        pass

while True:
    if not internet():
        time_sleep(refresh_offline)
        print("NO INTERNET")
        continue
    
    #system_commands.refresh_data_cached()
    refresh_alarms()
    break
