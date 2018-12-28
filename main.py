#!/usr/bin/env python3
import contextlib

from habitica import score_task, get_task
import timers

import importlib
pygame_spec = importlib.util.find_spec("pygame")
if pygame_spec is not None:
    with contextlib.redirect_stdout(None):
        from pygame import mixer
        pygame_enabled = True
else:
    pygame_enabled = False

import time
import sys

import configparser
config = configparser.ConfigParser()
config.read("config.ini")

def play_notification():
    if pygame_enabled:
        mixer.init()
        song = mixer.Sound("pomodoro.wav")
        mixer.Sound.play(song)
        time.sleep(21)
    else:
        print("Install Pygame for Audio notification")

def print_task_name(result, counts=False, notes=False, daily_task=False):
    if result:
        if counts:
            print("{:02d} | {}".format(result["counterUp"], result["text"]), end="")
        else:
            print(result["text"], end="")
        if daily_task:
            print(" (Daily: {})".format(daily_task), end="")
        if notes:
            print()
            if result["notes"]:
                for linea in result["notes"].splitlines():
                    print("\t{}".format(linea))

        else:
            print()
    else:
        print("Habitica API Error")


def print_item_drop(result):
    if "_tmp" in result:
        if "drop" in result["_tmp"]:
                print(result["_tmp"]["drop"]["dialog"])


def update_pomodoros(pomo_id, pomo_set_id=None, pomo_set_interval=4):
    # Scoring the basic Pomodoro
    r = score_task(pomo_id, True)

    if r:
        # Updating Pomodoro Set
        if pomo_set_id:
            if int(get_task(pomo_id)["counterUp"]) % pomo_set_interval == 0:
                set_r = score_task(pomo_set_id, True)
                if set_r:
                    print("You completed a new Pomodoro Set!")
                    print_item_drop(set_r)

        pomo_count = get_task(pomo_id)["counterUp"]
        if pomo_set_id:
            pomo_set_count = get_task(pomo_set_id)["counterUp"]
            print("Pomodoro: {} | Pomodoro Set: {}".format(pomo_count, pomo_set_count))
        else:
            print("Pomodoro: {}".format(pomo_count))
        print_item_drop(r)
    else:
        print("Habitica API Error when scoring")

    return r


def update_habit_and_daily(task_id, daily_id=None, daily_task_list=None, pomo_set_interval=4):
    # Scoring the task
    r = score_task(task_id, True)

    if r:
        print("La tarea fue puntuada correctamente.")
        print("\tHP: {}".format(r["hp"]))
        print("\tExp (lv {}): {}".format(r["lvl"], r["exp"]))
        print_item_drop(r)

        #Updating dailies
        if daily_id:
            if daily_task_list:
                total_count = 0
                tasks_array = ""
                for task in daily_task_list:
                    daily_name = daily_task_list[task]["daily"]
                    count_r = get_task(daily_task_list[task]["id"])
                    total_count += count_r["counterUp"]
                    tasks_array += "\n\tTotal: {:02d} | {}".format(count_r["counterUp"], count_r["text"])
                if get_task(daily_id)["completed"]:
                    print("'{}' is already completed".format(daily_name))
                else:
                    print("Daily associated: {}".format(daily_name), end="")
                    print(tasks_array)
                    print("\t===============\n\tTotal: {:02d} / {:02d}".format(total_count, pomo_set_interval))
                    if total_count >= pomo_set_interval:
                        d_r = score_task(daily_id, True)
                        if d_r:
                            print("Daily task '{}' was completed!".format(daily_name))
                        else:
                            print("Habitica API Error when scoring the daily")

            else:
                print("Error: A list of tasks sharing the same daily was not send")

    else:
        print("Habitica API Error when scoring the habit")

    return r


def main():
    # State: 0 exit | 1 menu | 2 post-menu | 3 pomodoro | 4 post-pomodoro | 5 descanso
    state = 0
    current_task = None
    task_list = dict()

    for t in config.items("HabiticaHabits"):
        task_key = t[0]
        task_info = t[1].split(",")
        task_list[task_key] = {"id": task_info[0], "daily": task_info[1] if len(task_info) > 1 else None}

    if len(sys.argv) < 2:
        state = 1
    else:
        current_task = sys.argv[1]
        state = 2

    while state:
        # Menu
        if state == 1:
            print("Main menu: <code> The task code <list> List of task codes <exit> Exit the menu")
            current_task = input("Input the task code: ")
            state = 2
        # Evaluating Menu input
        elif state == 2:
            if current_task == "list":
                print("pomo : -- | Basic Pomodoro Timer")
                for task_key in task_list:
                    r = get_task(task_list[task_key]["id"])
                    print(task_key + " : ", end="")
                    print_task_name(r, counts=True, daily_task=task_list[task_key]["daily"])
                print()
                state = 1
            elif current_task == "exit":
                state = 0
            elif current_task == "pomo":
                current_task = None
                state = 3
            else:
                if current_task not in task_list:
                    print("invalid task code")
                    current_task = None
                    state = 1
                else:
                    state = 3
        # Pomodoro State
        elif state == 3:
            if current_task:
                r = get_task(task_list[current_task]["id"])
                print_task_name(r, counts=True, notes=True)
            else:
                print("Basic Pomodoro Timer")
            is_interrupted = timers.timeout_input(int(config.get("Pomodoro", "TaskMinutes")), "Press Intro for stop")
            if is_interrupted:
                print("\x1b[2K\rTask was interrupted before time")
            else:
                if current_task:
                    # Updating basic pomodoro
                    if config.has_option("HabiticaPomodoro", "PomodoroSetID"):
                        r = update_pomodoros(config.get("HabiticaPomodoro", "PomodoroID"),
                                             config.get("HabiticaPomodoro", "PomodoroSetID"),
                                             int(config.get("Pomodoro", "TotalSet")))
                    else:
                        r = update_pomodoros(config.get("HabiticaPomodoro", "PomodoroID"))

                    # Scoring the task
                    target_task_daily_name = task_list[current_task]["daily"]
                    target_daily_task_list = {}
                    for task in task_list:
                        if task_list[task]["daily"] == target_task_daily_name:
                            target_daily_task_list[task] = task_list[task]

                    if target_task_daily_name:
                        if target_task_daily_name in dict(config.items("HabiticaDailies")):
                            rr = update_habit_and_daily(task_list[current_task]["id"],
                                                        config.get("HabiticaDailies", target_task_daily_name),
                                                        target_daily_task_list,
                                                        int(config.get("Pomodoro", "TotalSet")))
                        else:
                            print("Error: The associated task's daily {} does not exist".format(target_task_daily_name))
                            rr = update_habit_and_daily(task_list[current_task]["id"])
                    else:
                        rr = update_habit_and_daily(task_list[current_task]["id"])

                    if r and rr:
                        play_notification()
                else:
                    print("Completed Pomodoro!")
                    play_notification()
            state = 1
        elif state == 4:
            pass
        else:
            print("Warning: Bad state")


if __name__  ==  '__main__':
    main()
