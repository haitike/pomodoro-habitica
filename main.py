#!/usr/bin/python3
import sys
import tkinter as tk
from tkinter import Tk
import pomodoro_window
import config_tasks_window
import api_detail_window
import habitica
import configparser
import os

script_dir = os.path.dirname(__file__)
config_file = os.path.join(script_dir, "config.ini")
config = configparser.ConfigParser()
config.read(config_file)

def main():
    args = sys.argv[1:]

    user = habitica.User(verbose=True)
    if all([config.has_section("HabiticaAPI"), config.has_option("HabiticaAPI", "UserID"), config.has_option("HabiticaAPI", "APIKey")]):
        user.set_headers(config.get("HabiticaAPI", "UserID"), config.get("HabiticaAPI", "APIKey"))
        user.update_profile()

    if not user.username:
        root = Tk()
        root.title("API information")
        api_detail_window.APIDetails(root, user).pack(side="top", fill="both", expand=True)
        root.mainloop()

    if user.username:
        if not all([config.has_section("HabitList"), config.has_section("HabitDailys"), config.has_section("HabitCodes")]):
            root = Tk()
            root.title("Task configuration")
            cwindow = config_tasks_window.ConfigTasks(root, user.headers)
            cwindow.pack(side="top", fill="both", expand=True)
            root.mainloop()
            # Updating config after writting a lot of stuff in the window
            config.read(config_file)

        if all([config.has_section("HabitList"), config.has_section("HabitDailys"), config.has_section("HabitCodes")]):
            sess_mts = 25
            sbreak_mts = 5
            lbreak_mts = 25
            pomoset_amnt = 4
            if config.has_section("Pomodoro"):
                sess_mts = int(config.get("Pomodoro", "SessionMinutes"))
                sbreak_mts = int(config.get("Pomodoro", "ShortBreakMinutes"))
                lbreak_mts = int(config.get("Pomodoro", "LongBreakMinutes"))
                pomoset_amnt = int(config.get("Pomodoro", "PomoSetAmount"))
            bpomo_id = None
            bpomoset_id = None
            if config.has_option("BasicPomodoros", "PomoID"):
                bpomo_id = config.get("BasicPomodoros", "PomoID")
            if config.has_option("BasicPomodoros", "PomoSetID"):
                bpomoset_id = config.get("BasicPomodoros", "PomoSetID")

            # Habits
            user.create_basic_pomo_habits(bpomo_id, bpomoset_id)
            for id in config.items("HabitList"):
                user.habits[id[0]] = habitica.Habit(id[0], user.headers)
                if config.has_option("HabitDailys", id[0]):
                    user.habits[id[0]].daily = config.get("HabitDailys", id[0])
                if config.has_option("HabitCodes", id[0]):
                    user.habits[id[0]].code = config.get("HabitCodes", id[0])
            user.generate_dailys()

            # Main Window
            root = Tk()
            root.title("Pomodoro Habitica")
            pomo = pomodoro_window.Pomodoro(root, user)
            pomo.pack(side="top", fill="both", expand=True)
            if args:
                if args[0] == "fast": # For debugging
                    pomo.seconds_in_minute = 1
            pomo.set_config(sess_mts, sbreak_mts, lbreak_mts, pomoset_amnt)
            root.mainloop()


if __name__ == "__main__":
    main()
