#!/usr/bin/python3


import sys
from tkinter import Tk
from pomodoro import Pomodoro
from habitica import User
import configparser

config = configparser.ConfigParser()
config.read("config.ini")


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
        user = User(config.get("HabiticaAPI", "UserID"), config.get("HabiticaAPI", "APIKey"),
                    bpomo_id=config.get("BasicPomodoros", "PomoID"),
                    bpomoset_id=config.get("BasicPomodoros", "PomoSetID"))
        pomo = Pomodoro(root, user)
        pomo.pack(side="top", fill="both", expand=True)
        pomo.set_config(int(config.get("Pomodoro", "SessionMinutes")), int(config.get("Pomodoro", "ShortBreakMinutes")),
                        int(config.get("Pomodoro", "LongBreakMinutes")), int(config.get("Pomodoro", "PomoSetAmount")))
    root.mainloop()


if __name__ == "__main__":
    main()
