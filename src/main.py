#!/usr/bin/python3
import logging
from datetime import datetime
from display import Display
import system_commands

logging.basicConfig(level=logging.DEBUG)

try:
    from time import time as time_time, sleep as time_sleep
    starttime = time_time()
    
    
    print("Program starts")
    EPDisplay = Display()
    system_commands.set_pwr_led(0)
    while True:
        system_commands.set_pwr_led(1)
        
        print("Refresh", datetime.now())
        system_commands.set_pwr_led(0)
        
        if '06:00:00.000000' < str(datetime.now().time()) < '20:00:00.000000':
            EPDisplay.invert = False
            refresh_time = 180
        else:# If night do invert the screen, to see from the bed AND set refresh time to 20min=1200sec
            refresh_time = 1200
            EPDisplay.invert = True
        
        EPDisplay.refresh()
        
        print("Refresh every ",refresh_time,"sec")
        time_to_sleep = refresh_time - ((time_time() - starttime) % refresh_time)
        time_sleep(time_to_sleep)

finally:
    print("Program ended.")
    EPDisplay.exit()
