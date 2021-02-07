import keyboard


bt_volume_down = 'f14'
bt_volume_mute = 'f13'
bt_volume_up = 'help'
bt_volume_push_start = 0


def volume_down(key):
    global bt_volume_push_start
    if key.event_type == "down":
        bt_volume_push_start = key.time
    else:
        print('Down')
        elapsed_time = key.time - bt_volume_push_start
        print(elapsed_time)


def volume_mute(key):
    global bt_volume_push_start
    if key.event_type == "up":
        print('Mute')


def volume_up(key):
    global bt_volume_push_start
    if key.event_type == "down":
        bt_volume_push_start = key.time
    else:
        print('Up')
        elapsed_time = key.time - bt_volume_push_start
        print(elapsed_time)


# keyboard.hook_key(bt_volume_down, volume_down)
# keyboard.hook_key(bt_volume_mute, volume_mute)
# keyboard.hook_key(bt_volume_up, volume_up)

print('Toto')

try:
    print(keyboard.read_event())
    # keyboard.wait()
except Exception as e:
    print(e)
    keyboard.unhook_all_hotkeys()
