import tkinter as tk
import configparser
from functools import partial
from tkinter.font import nametofont

from habitica import get_user_tasks, get_tasks_order, Habit, Daily

class ConfigTasks(tk.Frame):
    def __init__(self, parent, headers, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        habits, dailys = get_user_tasks(headers)
        tasks_order = get_tasks_order(headers)

        # Config
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        if not self.config.has_section("HabitList"):
            self.config.add_section("HabitList")
        if not self.config.has_section("HabitDailys"):
            self.config.add_section("HabitDailys")
        if not self.config.has_section("HabitCodes"):
            self.config.add_section("HabitCodes")

        # The list of Dailys that will be choosen in the optionmenu.
        self.daily_dropmenu_choices = {None: "---"}
        self.task_rows = dict()
        for d_id in tasks_order["dailys"]:
            self.daily_dropmenu_choices[d_id] = dailys[d_id].text

        # Top level background and Save all button.
        self.configure(bg="light gray")
        self.grid(sticky="news")
        save_btn = tk.Button(self, text="Save all", command=self.save_all)
        save_btn.grid(row=3, column=0)

        # Create a frame for the canvas with non-zero row&column weights
        frame_canvas = tk.Frame(self)
        frame_canvas.grid(row=2, column=0, pady=(5, 0), sticky='nw')
        frame_canvas.grid_rowconfigure(0, weight=1)
        frame_canvas.grid_columnconfigure(0, weight=1)
        frame_canvas.grid_propagate(False)

        # Add a canvas in that frame
        canvas = tk.Canvas(frame_canvas) #Optional: bg="color"
        canvas.grid(row=0, column=0, sticky="news")

        # Link a scrollbar to the canvas
        scroll_bar = tk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
        scroll_bar.grid(row=0, column=1, sticky='ns')
        canvas.configure(yscrollcommand=scroll_bar.set)

        # Create a frame to contain the widgets
        interior_frame = tk.Frame(canvas) #Optional: bg="color"
        canvas.create_window((0, 0), window=interior_frame, anchor='nw')

        # Creating Widgets in the Scrollable frame
        for index, h_id in enumerate(tasks_order["habits"]):
            self.task_rows[h_id] = dict()

            # Variables
            self.task_rows[h_id]["is_pomo_var"] = tk.BooleanVar()
            self.task_rows[h_id]["daily_var"] = tk.StringVar()
            self.task_rows[h_id]["code_var"] = tk.StringVar()

            if self.config.has_option("HabitList", h_id):
                self.task_rows[h_id]["is_pomo_var"].set(self.config.getboolean("HabitList", h_id))

            if self.config.has_option("HabitDailys", h_id):
                self.task_rows[h_id]["daily_var"].set(self.daily_dropmenu_choices[self.config.get("HabitDailys", h_id)])
            else:
                self.task_rows[h_id]["daily_var"].set("---")

            if self.config.has_option("HabitCodes", h_id):
                self.task_rows[h_id]["code_var"].set(self.config.get("HabitCodes", h_id))

            # Widgets
            name = tk.Label(interior_frame, text=habits[h_id].text)
            if not habits[h_id].up:
                name.config(fg="red", text="{} (no Up task)".format(name.cget("text")))
            name.grid(row=index+1, column=1, sticky="news")
            is_pomo = tk.Checkbutton(interior_frame, text="Pomodoro", command=partial(self.is_pomo_check, h_id),
                                     variable=self.task_rows[h_id]["is_pomo_var"])
            is_pomo.grid(row=index + 1, column=2)
            self.task_rows[h_id]["daily"] = tk.OptionMenu(interior_frame, self.task_rows[h_id]["daily_var"], *self.daily_dropmenu_choices.values())
            self.task_rows[h_id]["daily"].grid(row=index + 1, column=3)
            self.set_max_width(self.daily_dropmenu_choices, self.task_rows[h_id]["daily"])
            code_label = tk.Label(interior_frame, text="Code ")
            code_label.grid(row=index + 1, column=4)
            self.task_rows[h_id]["code"] = tk.Entry(interior_frame, textvariable=self.task_rows[h_id]["code_var"], width=4)
            self.task_rows[h_id]["code"].grid(row=index + 1, column=5)

            # Disable widgets if pomocheck is not checked.
            self.is_pomo_check(h_id)

        # Update interior frame and set the canvas scrolling region
        interior_frame.update_idletasks()
        widgets_width = sum([name.winfo_width(), is_pomo.winfo_width(), code_label.winfo_width(),
                             self.task_rows[h_id]["daily"].winfo_width(), self.task_rows[h_id]["code"].winfo_width()])
        widgets_height = parent.winfo_screenheight() * 0.8
        frame_canvas.config(width=widgets_width + scroll_bar.winfo_width() + 20, height=widgets_height)
        canvas.config(scrollregion=canvas.bbox("all"))

    def set_max_width(self, stringList, element):
        f = nametofont(element.cget("font"))
        zerowidth = f.measure("0")
        w = max([f.measure(i) for i in stringList.values()]) / zerowidth
        element.config(width=int(w))

    def is_pomo_check(self, row_id):
        if self.task_rows[row_id]["is_pomo_var"].get():  # whenever checked
            self.task_rows[row_id]["code"].config(state=tk.NORMAL)
            self.task_rows[row_id]["daily"].config(state=tk.NORMAL)
        else:  # whenever unchecked
            self.task_rows[row_id]["code"].config(state=tk.DISABLED)
            self.task_rows[row_id]["daily"].config(state=tk.DISABLED)

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

        self.parent.destroy()
