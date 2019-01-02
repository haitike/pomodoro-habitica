#!/usr/bin/env python3
import contextlib
import time
from importlib import util

import menu
import habitica

import configparser
config = configparser.ConfigParser()
config.read("config.ini")

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

    menu_state_1 = menu.MenuState("Main Menu", input_text="Input one code")
    menu_state_1.append_item(menu.StateItem("b", "Basic pomodoro", print_test))
    for habit in user.get_habits():
        menu_state_1.append_item(menu.StateItem("x", habit.get_line_text()))
    menu_state_1.append_item(menu.StateExitItem("e", "Exists"))

    main_menu.append_state(menu_state_1)
    main_menu.start_main_loop()


if __name__  ==  '__main__':
    main()
