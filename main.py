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
root.geometry('400x360')

# labels
# Frames
#main_frame = tk.Frame(root)
#main_frame.grid(row=3, column=5, sticky='nesw')

# column padding in window
#root.grid_columnconfigure(1, weight=1)
#root.grid_columnconfigure(2, weight=1)
#root.grid_columnconfigure(3, weight=1)
#root.grid_columnconfigure(4, weight=3)

# row padding in window
#root.grid_rowconfigure(1, weight=1)
#root.grid_rowconfigure(2, weight=1)
#root.grid_rowconfigure(3, weight=1)

#placeholder_label = tk.Label(main_frame, text=' ~ ')
#placeholder_label.grid(row=3, column=2)

# Widgets
user_info_label_list = list()
for line in user.get_stats_text(tab_format=False).splitlines():
    user_info_label_list.append(tk.Label(root, text=line))
time_label = tk.Label(root, text='00:00')
status_label = tk.Label(root, text='Stopped')
streak_label = tk.Label(root, text='Streak: 0')
start_btn = tk.Button(root, text="Start", command=start)
interrupt_btn = tk.Button(root, text="Interrupt")
reset_btn = tk.Button(root, text="Stop", command=stop_count)

radio_var = tk.IntVar(root)
habit_radio_list = [tk.Radiobutton(root, text="Basic Pomo", variable=radio_var)]
habit_counter_label_list = [tk.Label(root)]
habit_dailys_label_list = [tk.Label(root)]
for habit in user.get_habits():
    habit_radio_list.append(tk.Radiobutton(root, text=habit.get_text(), variable=radio_var))
    counters = habit.get_counters()
    habit_counter_label_list.append(tk.Label(root, text="{}/{}".format(counters[0], counters[1])))
    habit_dailys_label_list.append(tk.Label(root, text=",".join(habit.get_tag_names())))


# Grid Left
for row_index_left, label in enumerate(user_info_label_list):
    label.grid(row=row_index_left+1, column=1, sticky='w')
time_label.grid(row=row_index_left+3, column=1, columnspan=2)
status_label.grid(row=row_index_left+4, column=1, sticky='w')
streak_label.grid(row=row_index_left+5, column=1, sticky='w')

# Grid Right
start_btn.grid(row=1, column=3)
interrupt_btn.grid(row=1, column=4)
reset_btn.grid(row=1, column=5)
for row_index_right, radio in enumerate(habit_radio_list):
    habit_radio_list[row_index_right].grid(row=row_index_right+2, column=3, columnspan=1)
    habit_counter_label_list[row_index_right].grid(row=row_index_right+2, column=4, columnspan=1)
    habit_dailys_label_list[row_index_right].grid(row=row_index_right+2, column=5, columnspan=1)


#habit_menu.configure(takefocus=1)

# MAINLOOP
root.mainloop()