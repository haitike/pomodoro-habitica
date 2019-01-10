import tkinter as tk
import configparser
from functools import partial

class ConfigTasks(tk.Frame):
    def __init__(self, parent, tasks, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        habits, dailys = tasks
        self.daily_dropmenu_choices = {None: "---"}
        self.task_rows = dict()

        # Config
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        if not self.config.has_section("HabitList"):
            self.config.add_section("HabitList")
        if not self.config.has_section("HabitDailys"):
            self.config.add_section("HabitDailys")
        if not self.config.has_section("HabitCodes"):
            self.config.add_section("HabitCodes")

        for d_id in dailys:
            self.daily_dropmenu_choices[d_id] = dailys[d_id].text

        for index, h_id in enumerate(habits):
            self.task_rows[h_id] = dict()
            self.task_rows[h_id]["name"] = tk.Label(self, text=habits[h_id].text)
            self.task_rows[h_id]["name"].grid(row=index+1, column=1)
            self.task_rows[h_id]["is_pomo_var"] = tk.BooleanVar()
            if self.config.has_option("HabitList", h_id):
                self.task_rows[h_id]["is_pomo_var"].set(self.config.getboolean("HabitList", h_id))
            self.task_rows[h_id]["is_pomo"] = tk.Checkbutton(self, text="Pomodoro", command=partial(self.is_pomo_check, h_id),
                                                             variable=self.task_rows[h_id]["is_pomo_var"])
            self.task_rows[h_id]["is_pomo"].grid(row=index + 1, column=2)
            self.task_rows[h_id]["daily_var"] = tk.StringVar()
            if self.config.has_option("HabitDailys", h_id):
                self.task_rows[h_id]["daily_var"].set(self.daily_dropmenu_choices[self.config.get("HabitDailys", h_id)])
            else:
                self.task_rows[h_id]["daily_var"].set("---")
            self.task_rows[h_id]["daily"] = tk.OptionMenu(self, self.task_rows[h_id]["daily_var"], *self.daily_dropmenu_choices.values())
            self.task_rows[h_id]["daily"].grid(row=index + 1, column=3)
            self.task_rows[h_id]["code_label"] = tk.Label(self, text="Code ")
            self.task_rows[h_id]["code_label"].grid(row=index + 1, column=4)
            self.task_rows[h_id]["code_var"] = tk.StringVar()
            if self.config.has_option("HabitCodes", h_id):
                self.task_rows[h_id]["code_var"].set(self.config.get("HabitCodes", h_id))
            self.task_rows[h_id]["code"] = tk.Entry(self, textvariable=self.task_rows[h_id]["code_var"], width=3)
            self.task_rows[h_id]["code"].grid(row=index + 1, column=5)

            self.is_pomo_check(h_id)

        self.save_btn = tk.Button(self, text="Save all", command=self.save_all)
        self.save_btn.grid(row=index + 2, column=1)

    def is_pomo_check(self, row_id):
        if self.task_rows[row_id]["is_pomo_var"].get():  # whenever checked
            self.task_rows[row_id]["code"].config(state=tk.NORMAL)
        else:  # whenever unchecked
            self.task_rows[row_id]["code"].config(state=tk.DISABLED)

    def save_all(self):
        for id in self.task_rows:
            if self.task_rows[id]["is_pomo_var"].get():
                self.config.set("HabitList", id, "true")
            else:
                self.config.remove_option("HabitList", id)

            for k, v in self.daily_dropmenu_choices.items():
                if v == self.task_rows[id]["daily_var"].get():
                    daily_id = k
            if daily_id:
                self.config.set("HabitDailys", id, daily_id)
            else:
                self.config.remove_option("HabitDailys", id)

            code_all_text = self.task_rows[id]["code_var"].get().split()
            if code_all_text:
                self.config.set("HabitCodes", id, code_all_text[0])
            else:
                self.config.remove_option("HabitCodes", id)

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
