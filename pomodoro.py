import tkinter as tk
from tkinter import messagebox


class Pomodoro(tk.Frame):
    def __init__(self, parent, user, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        
        # Habitica User
        self.user = user

        # Habitica config
        self.seconds_in_minute = 1  # Change it for fast tests.
        self.session_scs = 25 * self.seconds_in_minute
        self.short_rest_scs = 5 * self.seconds_in_minute
        self.long_rest_scs = 25 * self.seconds_in_minute
        self.pomo_set_amount = 4

        # tells the program if the next session is going to be a break or not
        self.is_break = False

        # Others
        self.session_counter = 0
        self.job = None

        # Widgets left side
        self.user_info_label_list = list()
        for line in self.user.get_stats_text().splitlines():
            self.user_info_label_list.append(tk.Label(self, text=line))
        self.time_label = tk.Label(self, text='00:00')
        self.status_label = tk.Label(self, text='Stopped')
        self.streak_label = tk.Label(self, text='Streak: 0')
        self.other_actions_menubtn = tk.Menubutton(self, text="Other actions", relief=tk.RAISED)
        
        # Widgets Right side
        self.start_btn = tk.Button(self, text="Start", command=self.start)
        self.interrupt_btn = tk.Button(self, text="Interrupt")
        self.reset_btn = tk.Button(self, text="Reset", command=self.stop_count)
        self.radio_var = tk.StringVar()
        self.radio_var.set("pomo")
        bpomo = self.user.basic_pomo
        if bpomo:
            self.bpomo_radio = tk.Radiobutton(self, text=bpomo.text, variable=self.radio_var, value="pomo")
            self.bpomo_counter_label = tk.Label(self, text="{}/{}".format(bpomo.counter_up, bpomo.counter_down))
        else:
            self.bpomo_radio = tk.Radiobutton(self, text="Basic Pomodoro", variable=self.radio_var, value="pomo")
            self.bpomo_counter_label = tk.Label(self, text="")
        self.habit_radio_list = list()
        self.habit_counter_label_list = list()
        self.habit_dailys_label_list = list()
        for id in self.user.habits:
            self.habit_radio_list.append(tk.Radiobutton(self, text=self.user.habits[id].text, variable=self.radio_var, value=id))
            self.habit_counter_label_list.append(tk.Label(self, text="{}/{}".format(self.user.habits[id].counter_up, self.user.habits[id].counter_down)))
            self.habit_dailys_label_list.append(tk.Label(self, text=",".join(self.user.habits[id].get_tag_names())))

        # Grid Left side
        for row_index_left, label in enumerate(self.user_info_label_list):
            label.grid(row=row_index_left+1, column=1, sticky='w')
        self.time_label.grid(row=row_index_left+3, column=1, columnspan=2, rowspan=2, sticky='nwse')
        self.status_label.grid(row=row_index_left+5, column=1, sticky='w')
        self.streak_label.grid(row=row_index_left+6, column=1, sticky='w')
        self.other_actions_menubtn.grid(row=row_index_left+ 8, column=1)

        # Grid Right side
        self.start_btn.grid(row=1, column=3)
        self.interrupt_btn.grid(row=1, column=4)
        self.reset_btn.grid(row=1, column=5)
        self.bpomo_radio.grid(row=2, column=3, sticky='w')
        self.bpomo_counter_label.grid(row=2, column=4, sticky='w')
        for row_index_right, radio in enumerate(self.habit_radio_list):
            self.habit_radio_list[row_index_right].grid(row=row_index_right+4, column=3, sticky='w')
            self.habit_counter_label_list[row_index_right].grid(row=row_index_right+4, column=4, sticky='w')
            self.habit_dailys_label_list[row_index_right].grid(row=row_index_right+4, column=5, sticky='w')

    def set_config(self, sess_mts, srest_mts, lgrest_mts, set_amnt):
        self.session_scs = sess_mts * self.seconds_in_minute
        self.short_rest_scs = srest_mts * self.seconds_in_minute
        self.long_rest_scs = lgrest_mts * self.seconds_in_minute
        self.pomo_set_amount = set_amnt * self.seconds_in_minute

    def count(self, timer):
        if timer <= -1:

            # toggle is break
            self.is_break = not self.is_break

            # prompt and start new session
            if self.is_break and self.session_counter % 4 != 0:
                exp, gold, lvl = self.user.exp, self.user.gold, self.user.lvl
                success_text = ""
                drops = list()
                if self.radio_var.get() == "pomo":
                    if self.user.basic_pomo:
                        drops = self.user.score_basic_pomo()
                else:
                    drops = self.user.score_habit(self.radio_var.get())
                if self.user.lvl > lvl:
                    success_text += "Level up! You are now level {}!!\n".format(self.user.lvl)
                success_text += "Exp: {:+.2f} Gold: {:+.2f} \n".format(self.user.exp - exp, self.user.gold - gold)
                if drops:
                    success_text += "Drops: {}\n".format(drops)
                prompt_answer = messagebox.askquestion("Session Ended!", success_text + "Are you ready for a break?", icon='question')
            elif self.is_break and self.session_counter % 4 == 0:
                prompt_answer = messagebox.askquestion("4 POMODORI!", "Do you think you deserve a very long break", icon='question')
            else:
                prompt_answer = messagebox.askquestion("Time's up!", "Ready for a new session?", icon='question')

            # prompts and restart cycle
            if prompt_answer == 'yes' and self.session_counter % 4 != 0 and self.is_break:
                self.after_cancel(self.job)
                self.count(self.short_rest_scs)
            elif prompt_answer == 'yes' and self.session_counter % 4 == 0 and self.is_break:
                self.after_cancel(self.job)
                self.count(self.long_rest_scs)
            elif prompt_answer == 'no':
                self.stop_count()
            else:
                self.session_counter += 1
                self.count(self.session_scs)
            return

        m, s = divmod(timer, 60)
        self.time_label.configure(text='{:02d}:{:02d}'.format(m, s))
        if self.is_break:
            self.streak_label.configure(text='BREAK!')
        else:
            self.streak_label.configure(text='Streak: {}'.format(self.session_counter))
        self.job = self.after(1000, self.count, timer - 1)

    # stops the countdown and resets the counter
    def stop_count(self):
        self.after_cancel(self.job)
        self.time_label.configure(text='{:02d}:{:02d}'.format(0, 0))
        self.session_counter = 0
        self.is_break = False
        self.streak_label.configure(text='Streak: {}'.format(0))
        self.start_btn.grid()
        self.bpomo_radio.grid()
        self.bpomo_counter_label.grid()
        for index, widget in enumerate(self.habit_radio_list):
            self.habit_radio_list[index].grid()
            self.habit_counter_label_list[index].grid()
            self.habit_dailys_label_list[index].grid()
        #self.start_btn.configure(text="Start", command=lambda: self.start())

    # starts counting loop
    def start(self):
        self.session_counter += 1
        self.start_btn.grid_remove()
        #self.start_btn.configure(command=tk.DISABLED)
        self.count(self.session_scs)
        self.bpomo_radio.grid_remove()
        self.bpomo_counter_label.grid_remove()
        for index, widget in enumerate(self.habit_radio_list):
            self.habit_radio_list[index].grid_remove()
            self.habit_counter_label_list[index].grid_remove()
            self.habit_dailys_label_list[index].grid_remove()

