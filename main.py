#!/usr/bin/python3

# Import libraries
import tkinter as tk
from tkinter import messagebox

import habitica
import configparser
config = configparser.ConfigParser()
config.read("config.ini")

# FUNCTIONS


# Countdown
def count(timer):
    global is_break
    global job
    global SESS_COUNTER

    if timer <= -1:

        # toggle is break
        is_break = not is_break

        # prompt and start new session
        if is_break and SESS_COUNTER % 4 != 0:
            prompt_answer = messagebox.askquestion("Session Ended!", "Are you ready for a break?", icon='question')
        elif is_break and SESS_COUNTER % 4 == 0:
            prompt_answer = messagebox.askquestion("4 POMODORI!", "Do you think you deserve a very long break", icon='question')
        else:
            prompt_answer = messagebox.askquestion("Time's up!", "Ready for a new session?", icon='question')


        # prompts and restart cycle
        if prompt_answer == 'yes' and SESS_COUNTER % 4 != 0 and is_break:
            root.after_cancel(job)
            count(SHORT_BREAK)
        elif prompt_answer == 'yes' and SESS_COUNTER % 4 == 0 and is_break:
            root.after_cancel(job)
            count(LONG_BREAK)
        elif prompt_answer == 'no':
            stop_count()
        else:
            SESS_COUNTER += 1
            count(SESSION)
        return

    m, s = divmod(timer, 60)
    time_label.configure(text='{:02d}:{:02d}'.format(m, s))
    if is_break:
        cnt_label.configure(text='BREAK!')
    else:
        cnt_label.configure(text='Streak: {}'.format(SESS_COUNTER))
    job = root.after(1000, count, timer - 1)


# stops the countdown and resets the counter
def stop_count():
    global SESS_COUNTER
    global is_break

    root.after_cancel(job)
    time_label.configure(text='{:02d}:{:02d}'.format(0, 0))
    SESS_COUNTER = 0
    is_break = False
    cnt_label.configure(text='Streak: {}'.format(0))
    start_btn.configure(text="Start", command=lambda: start())


# starts counting loop
def start():
    global SESSION
    global SESS_COUNTER

    SESS_COUNTER += 1
    start_btn.configure(command=tk.DISABLED)
    count(SESSION)


# VARIABLE DECLARATIONS
# define sessions and breaks
SHORT_BREAK = 5 * 1  # 5 mins after every pomodoro
LONG_BREAK = 20 * 1  # 20 mins after 4 pomodori
SESSION = 25 * 1  # lenght of a pomodoro session

# session counter
SESS_COUNTER = 0

# tells the program if the next session is going to be a break or not
is_break = False


# TKINTER SETTINGS

# Habitica
user = habitica.User(config.get("HabiticaAPI", "UserID"), config.get("HabiticaAPI", "APIKey"))

# root & title
root = tk.Tk()
root.title('Pomo')
root.geometry('180x160')

# labels
# main label area
main_label = tk.Frame(root)
main_label.grid(row=4, column=3, sticky='nesw')

# column padding in window
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)

# row padding in window
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)

# User info
user_info_label = tk.Label(main_label, text=user.get_stats_text(tab_format=False))
user_info_label.grid(row=1, column=1, columnspan=3)

# time label
time_label = tk.Label(main_label, text='00:00')
time_label.grid(row=2, column=1, columnspan=1)

# placehodler label
placeholder_label = tk.Label(main_label, text=' ~ ')
placeholder_label.grid(row=3, column=2)

# counter label
cnt_label = tk.Label(main_label, text='Streak: 0')
cnt_label.grid(row=2, column=3, columnspan=1)


# buttons
start_btn = tk.Button(main_label, text="Start", command=start)
start_btn.grid(row=3, column=1)
stop_btn = tk.Button(main_label, text="Stop", command=stop_count)
stop_btn.grid(row=3, column=3)

# Menu
menu_var = tk.StringVar(root)
menu_var.set("Basic Pomo")
habit_list = ["Basic Pomo"]
for habit in user.get_habits():
    habit_list.append(habit.get_line_text())

habit_menu = tk.OptionMenu(main_label, menu_var, *habit_list)
habit_menu.grid(row=4, column =1, columnspan=3)

# MAINLOOP
root.mainloop()
