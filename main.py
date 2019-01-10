#!/usr/bin/python3


import sys
from tkinter import Tk
from pomodoro_window import Pomodoro
from habitica import User
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

# Config variables
hab_id = config.get("HabiticaAPI", "UserID")
hab_key = config.get("HabiticaAPI", "APIKey")
sess_mts = int(config.get("Pomodoro", "SessionMinutes"))
sbreak_mts = int(config.get("Pomodoro", "ShortBreakMinutes"))
lbreak_mts = int(config.get("Pomodoro", "LongBreakMinutes"))
pomoset_amnt = int(config.get("Pomodoro", "PomoSetAmount"))
bpomo_id=None
bpomoset_id=None
if config.has_option("BasicPomodoros", "PomoID"):
    bpomo_id = config.get("BasicPomodoros", "PomoID")
if config.has_option("BasicPomodoros", "PomoSetID"):
    bpomoset_id = config.get("BasicPomodoros", "PomoSetID")

def main():
    args = sys.argv[1:]

    root = Tk()
    root.title("Pomodoro Habitica")
    # root.geometry('400x360')
    if args:
        # TODO: This is temporal. Pass argv in future.
        from tkinter import Frame, Label
        code = args[0]
        Frame(root).pack(side="top", fill="both", expand=True)
        Label(root, text=code).pack()
    else:
        user = User(hab_id, hab_key, bpomo_id, bpomoset_id)
        pomo = Pomodoro(root, user)
        pomo.pack(side="top", fill="both", expand=True)
        pomo.set_config(sess_mts, sbreak_mts, lbreak_mts, pomoset_amnt)
    root.mainloop()


if __name__ == "__main__":
    main()
