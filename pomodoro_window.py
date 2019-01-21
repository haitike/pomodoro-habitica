import tkinter as tk
from tkinter import messagebox
from notification import notification
import config_tasks_window

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

        # Config Task Window (Atribute used for checking if it is already created)
        self.config_task_window = None

        # Widgets left side
        self.user_name_label = tk.Label(self, text="")
        self.user_hp_label = tk.Label(self, text="")
        self.user_exp_label = tk.Label(self, text="")
        self.user_gold_label = tk.Label(self, text="")
        self.update_stats_labels()
        self.time_label = tk.Label(self, text='00:00')
        self.status_label = tk.Label(self, text='Stopped', fg="red")
        self.streak_label = tk.Label(self, text='Streak: 0')
        config_tasks_btn = tk.Button(self, text="Config Tasks", command=self.new_config_task_window)

        # Widgets Right side
        self.start_btn = tk.Button(self, text="Start", command=self.start)
        self.interrupt_btn = tk.Button(self, text="Interrupt")
        reset_btn = tk.Button(self, text="Reset", command=self.stop_count)
        self.radio_var = tk.StringVar()
        self.radio_var.set("bpomo_noid")
        self.bpomo_radio = tk.Radiobutton(self, text="Basic Pomodoro", variable=self.radio_var, value="bpomo_noid")
        self.bpomo_counter_label = tk.Label(self, text="")
        self.bpomoset_label = tk.Label(self, text="")
        self.bpomoset_counter_label = tk.Label(self, text="")
        if self.user:
            if self.user.basic_pomo:
                self.bpomo_radio.configure(text=self.user.basic_pomo.text, value="bpomo_id")
                self.bpomo_counter_label.configure(text="{}/{}".format(self.user.basic_pomo.counter_up, self.user.basic_pomo.counter_down))
                self.radio_var.set("bpomo_id")
                if self.user.basic_pomoset:
                    self.bpomoset_label.configure(text="\t{}".format(self.user.basic_pomoset.text))
                    self.bpomoset_counter_label.configure(text="{}/{}".format(self.user.basic_pomoset.counter_up, self.user.basic_pomoset.counter_down))
        self.habit_radio_list = list()
        self.habit_counter_label_list = list()
        self.habit_daily_label_list = list()
        self.habit_daily_counter_label_list = list()
        if self.user:
            for id in self.user.habits:
                self.habit_radio_list.append(tk.Radiobutton(self, text=self.user.habits[id].text, variable=self.radio_var, value=id))
                self.habit_counter_label_list.append(tk.Label(self, text="{}/{}".format(self.user.habits[id].counter_up, self.user.habits[id].counter_down)))
                daily_id = self.user.habits[id].daily
                if daily_id:
                    self.habit_daily_label_list.append(tk.Label(self, text=self.user.dailys[daily_id].text))
                    self.habit_daily_counter_label_list.append(tk.Label(self, text="{}/{}".format(self.user.daily_count(daily_id), self.pomo_set_amount)))
                else:
                    self.habit_daily_label_list.append(tk.Label(self, text=""))
                    self.habit_daily_counter_label_list.append(tk.Label(self, text=""))

        # Hidden
        self.current_task_info_label = tk.Label(self, text="")
        self.current_task_counter_label = tk.Label(self, text="")
        self.current_task_code_label = tk.Label(self, text="")
        self.current_task_notes_label = tk.Label(self, text="")
        # The Switch Task Option Menu
        if self.user:
            self.list_var = tk.StringVar()
            self.switch_task_label = tk.Label(self, text="Do you want to switch task after this break?")
            if self.user.basic_pomo:
                self.option_list = { self.user.basic_pomo.text : "bpomo_id"}
            else:
                self.option_list = { "Basic Pomodoro" : "bpomo_noid"}
            for id in self.user.habits:
                self.option_list[self.user.habits[id].text] = id
            self.switch_task_menu = tk.OptionMenu(self, self.list_var, *self.option_list)
            self.set_optionlist_from_radio()

        # Grid Left side
        self.user_name_label.grid(row=1, column=1, sticky='w')
        self.user_hp_label.grid(row=2, column=1, sticky='w')
        self.user_exp_label.grid(row=3, column=1, sticky='w')
        self.user_gold_label.grid(row=4, column=1, sticky='w')
        self.time_label.grid(row=6, column=1, columnspan=2, rowspan=2, sticky='nwse')
        self.status_label.grid(row=8, column=1, sticky='w')
        self.streak_label.grid(row=9, column=1, sticky='w')
        config_tasks_btn.grid(row=11, column=1)

        # Grid Right side
        self.start_btn.grid(row=1, column=3)
        self.interrupt_btn.grid(row=1, column=4)
        reset_btn.grid(row=1, column=5)
        self.bpomo_radio.grid(row=2, column=3, sticky='w')
        self.bpomo_counter_label.grid(row=2, column=4, sticky='w')
        self.bpomoset_label.grid(row=3, column=3, sticky='w')
        self.bpomoset_counter_label.grid(row=3, column=4, sticky='w')
        for row_index_right, radio in enumerate(self.habit_radio_list):
            self.habit_radio_list[row_index_right].grid(row=row_index_right+5, column=3, sticky='w')
            self.habit_counter_label_list[row_index_right].grid(row=row_index_right+5, column=4, sticky='w')
            self.habit_daily_label_list[row_index_right].grid(row=row_index_right + 5, column=5, sticky='w')
            self.habit_daily_counter_label_list[row_index_right].grid(row=row_index_right + 5, column=6, sticky='w')

        # Right hidden
        self.current_task_info_label.grid(row=2, column=3, sticky="w")
        self.current_task_counter_label.grid(row=2, column=4, sticky="w")
        self.current_task_code_label.grid(row=3, column=3, sticky="w")
        self.current_task_notes_label.grid(row=5, column=3, columnspan=3, sticky="w")
        if self.user:
            self.switch_task_label.grid(row=6, column=3, sticky="w")
            self.switch_task_menu.grid(row=7, column=3)
        self.current_task_info_label.grid_remove()
        self.current_task_counter_label.grid_remove()
        self.current_task_code_label.grid_remove()
        self.current_task_notes_label.grid_remove()
        if self.user:
            self.switch_task_label.grid_remove()
            self.switch_task_menu.grid_remove()
        # Update
        self.update_habit_labels()

    def set_config(self, sess_mts, srest_mts, lgrest_mts, set_amnt):
        self.session_scs = sess_mts * self.seconds_in_minute
        self.short_rest_scs = srest_mts * self.seconds_in_minute
        self.long_rest_scs = lgrest_mts * self.seconds_in_minute
        self.pomo_set_amount = set_amnt

    def count(self, timer):
        if timer <= -1:

            # toggle is break
            self.is_break = not self.is_break

            # prompt and start new session
            if self.is_break and self.session_counter % 4 != 0:
                if self.user:
                    success_text, scored_task = self.score_to_habitica()
                notification(0, task=scored_task if self.user is True else "")
                prompt_answer = messagebox.askquestion("Session Ended!", success_text if self.user is True else "" + "Are you ready for a break?", icon='question')
            elif self.is_break and self.session_counter % 4 == 0:
                if self.user:
                    success_text, scored_task = self.score_to_habitica()
                notification(0, task=scored_task if self.user is True else "")
                prompt_answer = messagebox.askquestion("4 POMODORI!", success_text if self.user is True else "" + "\nDo you think you deserve a very long break?", icon='question')
            else:
                notification(1)
                prompt_answer = messagebox.askquestion("Time's up!", "Ready for a new session?", icon='question')

            # prompts and restart cycle
            if prompt_answer == 'yes' and self.session_counter % 4 != 0 and self.is_break:
                self.after_cancel(self.job)
                self.count(self.short_rest_scs)
                self.status_label.config(text="Break", fg="orange")
                if self.user:
                    self.switch_task_label.grid()
                    self.switch_task_menu.grid()
            elif prompt_answer == 'yes' and self.session_counter % 4 == 0 and self.is_break:
                self.after_cancel(self.job)
                self.count(self.long_rest_scs)
                self.status_label.config(text="Long Break", fg="orange")
                if self.user:
                    self.switch_task_label.grid()
                    self.switch_task_menu.grid()
            elif prompt_answer == 'no':
                self.stop_count()
            else:
                self.status_label.config(text="Pomodoro", fg="green")
                if self.user:
                    self.set_radio_from_optionlist()
                self.update_current_task_labels()
                self.session_counter += 1
                self.count(self.session_scs)
                if self.user:
                    self.switch_task_label.grid_remove()
                    self.switch_task_menu.grid_remove()
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
            self.config_task_window = tk.Toplevel(self)
            ctask_frame = config_tasks_window.ConfigTasks(self.config_task_window, self.user.headers)
            ctask_frame.pack(side="top", fill="both", expand=True)

    def update_stats_labels(self):
        if self.user:
            self.user_name_label.configure(text="{} (lv{:.0f})".format(self.user.username, self.user.lvl))
            self.user_hp_label.configure(text="HP: {:.0f} / {}".format(self.user.hp, self.user.max_hp))
            self.user_exp_label.configure(text="Exp: {:.0f} / {}".format(self.user.exp, self.user.exp_next))
            self.user_gold_label.configure(text="Gold: {:.0f}".format(self.user.gold))

    def update_habit_labels(self):
        if self.user:
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
            daily_id = self.user.habits[id].daily
            if daily_id:
                self.habit_daily_label_list[index].configure(text=self.user.dailys[daily_id].text)
                self.habit_daily_counter_label_list[index].configure(text="{}/{}".format(self.user.daily_count(daily_id), self.pomo_set_amount))
                if self.user.dailys[daily_id].completed:
                    self.habit_daily_label_list[index].config(fg="green")
                    self.habit_daily_counter_label_list[index].config(fg="green")
                else:
                    self.habit_daily_label_list[index].config(fg="black")
                    self.habit_daily_counter_label_list[index].config(fg="black")

        # Labels when pomodoro is active
        self.update_current_task_labels()

    def score_to_habitica(self):
        exp, gold, lvl = self.user.exp, self.user.gold, self.user.lvl
        success_text = ""
        scored_task = ""

        if self.radio_var.get() != "bpomo_noid":
            if self.radio_var.get() == "bpomo_id":
                drops = self.user.score_basic_pomo(set_interval=self.pomo_set_amount, update_tasks=True)
                scored_task = self.user.basic_pomo.text
            else:
                drops = self.user.score_basic_pomo(set_interval=self.pomo_set_amount, update_tasks=True)
                drops += self.user.score_habit(self.radio_var.get(), set_interval=self.pomo_set_amount, update_tasks=True)
                scored_task = self.user.habits[self.radio_var.get()].text
            if self.user.lvl > lvl:
                success_text += "Level up! You are now level {}!!".format(self.user.lvl)
            else:
                success_text += "Exp: {:+.2f}".format(self.user.exp - exp)
            success_text += " Gold: {:+.2f} \n".format(self.user.gold - gold)
            if drops:
                success_text += "Drops: {}\n".format(drops)
            self.update_stats_labels()
            self.update_habit_labels()
        else:
            scored_task = "Basic Pomodoro"

        return success_text, scored_task

    # stops the countdown and resets the counter
    def stop_count(self):
        self.status_label.config(text="Stopped", fg="red")
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
            self.habit_daily_label_list[index].grid()
            self.habit_daily_counter_label_list[index].grid()
        #self.start_btn.configure(text="Start", command=lambda: self.start())
        self.current_task_info_label.configure(text="")
        self.current_task_counter_label.configure(text="")
        self.current_task_code_label.configure(text="")
        self.current_task_notes_label.configure(text="")
        self.current_task_info_label.grid_remove()
        self.current_task_counter_label.grid_remove()
        self.current_task_code_label.grid_remove()
        self.current_task_notes_label.grid_remove()
        if self.user:
            self.switch_task_label.grid_remove()
            self.switch_task_menu.grid_remove()

    # starts counting loop
    def start(self):
        self.status_label.config(text="Pomodoro", fg="green")
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
            self.habit_daily_label_list[index].grid_remove()
            self.habit_daily_counter_label_list[index].grid_remove()
        # self.start_btn.configure(command=tk.DISABLED)

        if self.user:
            self.set_optionlist_from_radio()

        self.update_current_task_labels()

        self.current_task_info_label.grid()
        self.current_task_counter_label.grid()
        self.current_task_code_label.grid()
        self.current_task_notes_label.grid()

    def set_optionlist_from_radio(self):
        for op in self.option_list:
            if self.option_list[op] == self.radio_var.get():
                self.list_var.set(op)

    def set_radio_from_optionlist(self):
        self.radio_var.set(self.option_list[self.list_var.get()])

    def update_current_task_labels(self):
        if self.radio_var.get() == "bpomo_noid":
            self.current_task_info_label.configure(text="Basic Pomodoro")
        elif self.radio_var.get() == "bpomo_id":
            self.current_task_info_label.configure(text=self.user.basic_pomo.text)
            self.current_task_counter_label.configure(text="{}/{}".format(self.user.basic_pomo.counter_up,
                                                                          self.user.basic_pomo.counter_down))
        else:
            self.current_task_info_label.configure(text=self.user.habits[self.radio_var.get()].text)
            self.current_task_counter_label.configure(
                text="{}/{}".format(self.user.habits[self.radio_var.get()].counter_up,
                                    self.user.habits[self.radio_var.get()].counter_down))
            if self.user.habits[self.radio_var.get()].code:
                self.current_task_code_label.configure(
                    text="Console code: {}".format(self.user.habits[self.radio_var.get()].code))
            self.current_task_notes_label.configure(text=self.user.habits[self.radio_var.get()].notes)
