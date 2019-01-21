#!/usr/bin/python3
import sys
from tkinter import messagebox
from tkinter import Tk
import pomodoro_window
import config_tasks_window
import api_detail_window
import habitica
import configparser
import os
import requests

script_dir = os.path.dirname(__file__)
config_file = os.path.join(script_dir, "config.ini")
config = configparser.ConfigParser()
config.read(config_file)

def main():
    # Args checking
    fast = False
    use_habitica = True
    for arg in sys.argv[1:]:
        if arg == "fast":
            fast = True # For debugging (Minutes are 1 second)
        if arg == "no-habitica":
            use_habitica = False

    if use_habitica:
        # Creating Habitica User
        try:
            user = habitica.User(verbose=True)
            if all([config.has_section("HabiticaAPI"), config.has_option("HabiticaAPI", "UserID"), config.has_option("HabiticaAPI", "APIKey")]):
                user.set_headers(config.get("HabiticaAPI", "UserID"), config.get("HabiticaAPI", "APIKey"))
                user.update_profile()

            # Create API details Window if it is not in the config file. (First time use)
            if not user.username:
                root = Tk()
                root.title("API information")
                api_detail_window.APIDetails(root, user).pack(side="top", fill="both", expand=True)
                root.mainloop()
        except requests.exceptions.SSLError:
            root = Tk()
            root.withdraw()
            prompt_answer = messagebox.askquestion("Error", "Connection with Habitica failed (SSL Error). Do you want to use Pomodoro without Habitica?")
            if prompt_answer == "yes":
                use_habitica = False
            else:
                return

    # If the API details are correct and can be connected to the server
    if use_habitica:
        if user.username:
            # Create the Configuration Window if it is the first time.
            if not all([config.has_section("HabitList"), config.has_section("HabitDailys"), config.has_section("HabitCodes")]):
                root = Tk()
                root.title("Task configuration")
                cwindow = config_tasks_window.ConfigTasks(root, user.headers)
                cwindow.pack(side="top", fill="both", expand=True)
                root.mainloop()
                # Updating config after writting a lot of stuff in the window
                config.read(config_file)

            # Normal application starts
            if all([config.has_section("HabitList"), config.has_section("HabitDailys"), config.has_section("HabitCodes")]):
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
        else:
            print("Username could not be retrieved")

    # Time Stuff
    sess_mts = 25
    sbreak_mts = 5
    lbreak_mts = 25
    pomoset_amnt = 4
    if config.has_section("Pomodoro"):
        sess_mts = int(config.get("Pomodoro", "SessionMinutes"))
        sbreak_mts = int(config.get("Pomodoro", "ShortBreakMinutes"))
        lbreak_mts = int(config.get("Pomodoro", "LongBreakMinutes"))
        pomoset_amnt = int(config.get("Pomodoro", "PomoSetAmount"))

    # Main Window
    root = Tk()
    root.title("Pomodoro Habitica")
    pomo = pomodoro_window.Pomodoro(root, user if use_habitica is True else None)
    pomo.pack(side="top", fill="both", expand=True)
    if fast:
        pomo.seconds_in_minute = 1
    pomo.set_config(sess_mts, sbreak_mts, lbreak_mts, pomoset_amnt)
    root.mainloop()


if __name__ == "__main__":
    main()
