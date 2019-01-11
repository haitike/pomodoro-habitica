import tkinter as tk
from tkinter import messagebox
from config_tasks_window import ConfigTasks


class Pomodoro(tk.Frame):
    def __init__(self, parent, user, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        
        # Habitica User
        self.user = user

        # Habitica config
        self.seconds_in_minute = 60  # Change it for fast tests.
        self.session_scs = 25 * self.seconds_in_minute
        self.short_rest_scs = 5 * self.seconds_in_minute
        self.long_rest_scs = 25 * self.seconds_in_minute
        self.pomo_set_amount = 4

        # tells the program if the next session is going to be a break or not
        self.is_break = False

        # Others
        self.session_counter = 0
        self.job = None

        # Config Task Window
        self.config_task_window = None

        # Widgets left side
        self.user_name_label = tk.Label(self, text="")
        self.user_hp_label = tk.Label(self, text="")
        self.user_exp_label = tk.Label(self, text="")
        self.user_gold_label = tk.Label(self, text="")
        self.update_stats_labels()
        self.time_label = tk.Label(self, text='00:00')
        self.status_label = tk.Label(self, text='Stopped')
        self.streak_label = tk.Label(self, text='Streak: 0')
        self.config_tasks_btn = tk.Button(self, text="Config Tasks", command=self.new_config_task_window)

        # Widgets Right side
        self.start_btn = tk.Button(self, text="Start", command=self.start)
        self.interrupt_btn = tk.Button(self, text="Interrupt")
        self.reset_btn = tk.Button(self, text="Reset", command=self.stop_count)
        self.radio_var = tk.StringVar()
        self.radio_var.set("bpomo_noid")
        self.bpomo_radio = tk.Radiobutton(self, text="Basic Pomodoro", variable=self.radio_var, value="bpomo_noid")
        self.bpomo_counter_label = tk.Label(self, text="")
        self.bpomoset_label = tk.Label(self, text="")
        self.bpomoset_counter_label = tk.Label(self, text="")
        if self.user.basic_pomo:
            self.bpomo_radio.configure(text=self.user.basic_pomo.text, value="bpomo_id")
            self.bpomo_counter_label.configure(text="{}/{}".format(self.user.basic_pomo.counter_up, self.user.basic_pomo.counter_down))
            self.radio_var.set("bpomo_id")
            if self.user.basic_pomoset:
                self.bpomoset_label.configure(text="\t{}".format(self.user.basic_pomoset.text))
                self.bpomoset_counter_label.configure(text="{}/{}".format(self.user.basic_pomoset.counter_up, self.user.basic_pomoset.counter_down))
        self.habit_radio_list = list()
        self.habit_counter_label_list = list()
        self.habit_dailys_label_list = list()
        for id in self.user.habits:
            self.habit_radio_list.append(tk.Radiobutton(self, text=self.user.habits[id].text, variable=self.radio_var, value=id))
            self.habit_counter_label_list.append(tk.Label(self, text="{}/{}".format(self.user.habits[id].counter_up, self.user.habits[id].counter_down)))
            self.habit_dailys_label_list.append(tk.Label(self, text=",".join(self.user.habits[id].get_tag_names())))
        # Hidden
        self.current_task_info_label = tk.Label(self, text="")
        self.current_task_counter_label = tk.Label(self, text="")
        self.current_task_notes_label = tk.Label(self, text="")

        # Grid Left side
        self.user_name_label.grid(row=1, column=1, sticky='w')
        self.user_hp_label.grid(row=2, column=1, sticky='w')
        self.user_exp_label.grid(row=3, column=1, sticky='w')
        self.user_gold_label.grid(row=4, column=1, sticky='w')
        self.time_label.grid(row=6, column=1, columnspan=2, rowspan=2, sticky='nwse')
        self.status_label.grid(row=8, column=1, sticky='w')
        self.streak_label.grid(row=9, column=1, sticky='w')
        self.config_tasks_btn.grid(row=11, column=1)

        # Grid Right side
        self.start_btn.grid(row=1, column=3)
        self.interrupt_btn.grid(row=1, column=4)
        self.reset_btn.grid(row=1, column=5)
        self.bpomo_radio.grid(row=2, column=3, sticky='w')
        self.bpomo_counter_label.grid(row=2, column=4, sticky='w')
        self.bpomoset_label.grid(row=3, column=3, sticky='w')
        self.bpomoset_counter_label.grid(row=3, column=4, sticky='w')
        for row_index_right, radio in enumerate(self.habit_radio_list):
            self.habit_radio_list[row_index_right].grid(row=row_index_right+5, column=3, sticky='w')
            self.habit_counter_label_list[row_index_right].grid(row=row_index_right+5, column=4, sticky='w')
            self.habit_dailys_label_list[row_index_right].grid(row=row_index_right+5, column=5, sticky='w')

        # Right hidden
        self.current_task_info_label.grid(row=2, column=3, sticky="w")
        self.current_task_counter_label.grid(row=2, column=4, sticky="w")
        self.current_task_notes_label.grid(row=4, column=3, columnspan=3, sticky="w")
        self.current_task_info_label.grid_remove()
        self.current_task_notes_label.grid_remove()

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
                success_text = self.score_to_habitica()
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

    def new_config_task_window(self):
        if self.config_task_window is None or not self.config_task_window.winfo_exists():
            self.config_task_window = tk.Toplevel(self.parent)
            self.config_task_frame = ConfigTasks(self.config_task_window, self.user.get_all_tasks())
            self.config_task_frame.pack(side="top", fill="both", expand=True)

    def update_stats_labels(self):
        self.user_name_label.configure(text="{} (lv{:.0f})".format(self.user.username, self.user.lvl))
        self.user_hp_label.configure(text="HP: {:.0f} / {}".format(self.user.hp, self.user.max_hp))
        self.user_exp_label.configure(text="Exp: {:.0f} / {}".format(self.user.exp, self.user.exp_next))
        self.user_gold_label.configure(text="Gold: {:.0f}".format(self.user.gold))

    def update_habit_labels(self):
        if self.user.basic_pomo:
            self.bpomo_radio.configure(text=self.user.basic_pomo.text)
            self.bpomo_counter_label.configure(text="{}/{}".format(self.user.basic_pomo.counter_up, self.user.basic_pomo.counter_down))
            if self.user.basic_pomoset:
                self.bpomoset_label.configure(text="\t{}".format(self.user.basic_pomoset.text))
                self.bpomoset_counter_label.configure(text="{}/{}".format(self.user.basic_pomoset.counter_up, self.user.basic_pomoset.counter_down))

        for index, row in enumerate(self.habit_radio_list):
            id = self.habit_radio_list[index].cget("value")
            self.habit_radio_list[index].configure(text=self.user.habits[id].text)
            self.habit_counter_label_list[index].configure(text="{}/{}".format(self.user.habits[id].counter_up, self.user.habits[id].counter_down))
            self.habit_dailys_label_list[index].configure(text=",".join(self.user.habits[id].get_tag_names()))

    def score_to_habitica(self):
        exp, gold, lvl = self.user.exp, self.user.gold, self.user.lvl
        success_text = ""

        if self.radio_var.get() != "bpomo_noid":
            if self.radio_var.get() == "bpomo_id":
                drops = self.user.score_basic_pomo(set_interval=self.pomo_set_amount, update_tasks=True)
            else:
                drops = self.user.score_basic_pomo(set_interval=self.pomo_set_amount, update_tasks=True)
                drops += self.user.score_habit(self.radio_var.get(), set_interval=self.pomo_set_amount, update_tasks=True)

            if self.user.lvl > lvl:
                success_text += "Level up! You are now level {}!!".format(self.user.lvl)
            else:
                success_text += "Exp: {:+.2f}".format(self.user.exp - exp)
            success_text += " Gold: {:+.2f} \n".format(self.user.gold - gold)
            if drops:
                success_text += "Drops: {}\n".format(drops)
            self.update_stats_labels()
            self.update_habit_labels()
        return success_text

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
        self.bpomoset_label.grid()
        self.bpomoset_counter_label.grid()
        for index, widget in enumerate(self.habit_radio_list):
            self.habit_radio_list[index].grid()
            self.habit_counter_label_list[index].grid()
            self.habit_dailys_label_list[index].grid()
        #self.start_btn.configure(text="Start", command=lambda: self.start())
        self.current_task_info_label.configure(text="")
        self.current_task_counter_label.configure(text="")
        self.current_task_notes_label.configure(text="")
        self.current_task_info_label.grid_remove()
        self.current_task_counter_label.grid_remove()
        self.current_task_notes_label.grid_remove()

    # starts counting loop
    def start(self):
        self.session_counter += 1
        self.start_btn.grid_remove()
        self.count(self.session_scs)
        self.bpomo_radio.grid_remove()
        self.bpomo_counter_label.grid_remove()
        self.bpomoset_label.grid_remove()
        self.bpomoset_counter_label.grid_remove()
        for index, widget in enumerate(self.habit_radio_list):
            self.habit_radio_list[index].grid_remove()
            self.habit_counter_label_list[index].grid_remove()
            self.habit_dailys_label_list[index].grid_remove()
        # self.start_btn.configure(command=tk.DISABLED)
        if self.radio_var.get() == "bpomo_noid":
            self.current_task_info_label.configure(text="Basic Pomodoro")
        elif self.radio_var.get() == "bpomo_id":
            self.current_task_info_label.configure(text=self.user.basic_pomo.text)
            self.current_task_counter_label.configure(text="{}/{}".format(self.user.basic_pomoset.counter_up,
                                                                          self.user.basic_pomoset.counter_down))
        else:
            self.current_task_info_label.configure(text=self.user.habits[self.radio_var.get()].text)
            self.current_task_counter_label.configure(text="{}/{}".format(self.user.habits[self.radio_var.get()].counter_up,
                                                                          self.user.habits[self.radio_var.get()].counter_down))
            self.current_task_notes_label.configure(text=self.user.habits[self.radio_var.get()].notes)
        self.current_task_info_label.grid()
        self.current_task_counter_label.grid()
        self.current_task_notes_label.grid()