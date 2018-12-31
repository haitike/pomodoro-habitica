#!/usr/bin/env python3
import contextlib
import time
import configparser
from importlib import util

import menu

pygame_spec = util.find_spec("pygame")
if pygame_spec is not None:
    with contextlib.redirect_stdout(None):
        from pygame import mixer
        pygame_enabled = True
else:
    pygame_enabled = False


# config = configparser.ConfigParser()
# config.read("config.ini")


def play_notification():
    if pygame_enabled:
        mixer.init()
        song = mixer.Sound("pomodoro.wav")
        mixer.Sound.play(song)
        time.sleep(21)
    else:
        print("Install Pygame for Audio notification")


def main():
    main_menu = menu.Menu()
    menu_state_1 = menu.MenuState("Main Menu", input_text="Input one code")
    menu_item_pomo = menu.StateItem("b", "Basic pomodoro", None)
    menu_item_exit = menu.StateItem("e", "Exits", None)

    menu_state_1.append_item(menu_item_pomo)
    menu_state_1.append_item(menu_item_exit)
    main_menu.append_state(menu_state_1)
    main_menu.start()


if __name__  ==  '__main__':
    main()
