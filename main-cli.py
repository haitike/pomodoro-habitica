#!/usr/bin/env python3
import contextlib
import time
from importlib import util

import menu
import habitica
import sys
import configparser
config = configparser.ConfigParser()
config.read("config.ini")

if sys.platform.startswith('win32'):
    print("Pomodoro timer is currently not supported in Windows. \nExiting...")
    exit()
elif sys.platform.startswith('linux'):
    # Linux-specific code here...
    pass
else:
    print("Warning: Your operative system may be not supported")

pygame_spec = util.find_spec("pygame")
if pygame_spec is not None:
    with contextlib.redirect_stdout(None):
        from pygame import mixer
        pygame_enabled = True
else:
    pygame_enabled = False


def print_test():
    print("basic pomo")


def play_notification():
    if pygame_enabled:
        mixer.init()
        song = mixer.Sound("pomodoro.wav")
        mixer.Sound.play(song)
        time.sleep(21)
    else:
        print("Install Pygame for Audio notification")


def main():
    user = habitica.User(config.get("HabiticaAPI", "UserID"), config.get("HabiticaAPI", "APIKey"))

    main_menu = menu.Menu()

    menu_state_1 = menu.State("Main Menu", input_text="Input one code")
    menu_state_1.append_item(menu.Item("Basic pomodoro", "b", print_test))
    for habit in user.habits:
        menu_state_1.append_item(menu.Item(habit.get_line_text(), habit.key_code))
    menu_state_1.append_item(menu.ExitItem("Exit", "e"))
    menu_state_1.append_item(menu.ExitItem("Exit"))

    main_menu.append_state(menu_state_1)
    main_menu.start_main_loop()
    print(user.get_all_text())


if __name__  ==  '__main__':
    main()
