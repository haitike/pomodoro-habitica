import json
import sys
import requests


class Task:
    def __init__(self, id, headers, retrieve_info=True, text=None, notes=None):
        self.id = id
        self.headers = headers
        self.type = "Task"
        self.tags = list()

        if retrieve_info:
            self.update()
        else:
            self.text = text
            self.notes = notes

    def get_tag_names(self):
        tag_names = list()
        for tag_id in self.tags:
            tag_names.append(self.tags[tag_id])
        return tag_names

    def retrieve_from_habitica(self):
        r = requests.get('https://habitica.com/api/v3/tasks/' + self.id, headers=self.headers)

        result = json.loads(r.content)
        if r.ok:
            if result["success"]:
                return result["data"]
            else:
                return False
        else:
            return False

    def update(self):
        info = self.retrieve_from_habitica()
        if info:
            self.text = info["text"]
            self.notes = info["notes"]

    def score(self, positive=True):
        data = {
            'type': 'task',
        }

        if positive:
            r = requests.post('https://habitica.com/api/v3/tasks/' + self.id +
                              '/score/up', headers=self.headers, data=data)
        else:
            r = requests.post('https://habitica.com/api/v3/tasks/' + self.id +
                              '/score/down', headers=self.headers, data=data)

        result = json.loads(r.content)
        if r.ok:
            if result["success"]:
                drop = None
                if "_tmp" in result["data"]:
                    if "drop" in result["data"]["_tmp"]:
                        drop = "{} ({})".format(result["data"]["_tmp"]["drop"]["key"], result["data"]["_tmp"]["drop"]["type"])
                return result["data"]["hp"], result["data"]["exp"], result["data"]["lvl"], result["data"]["gp"], drop
            else:
                return False
        else:
            return False

    def get_line_text(self):
        return "{:<31s}\t{}".format(self.text, ", ".join(self.get_tag_names()))


class Habit(Task):
    def __init__(self, id, headers, retrieve_info=True, text=None, notes=None, counter_up=None, counter_down=None):
        Task.__init__(self, id, headers, retrieve_info, text, notes)
        self.type = "Habit"

        if not retrieve_info:
            self.counter_up = counter_up
            self.counter_down = counter_down

    def update(self):
        info = self.retrieve_from_habitica()
        if info:
            self.text = info["text"]
            self.notes = info["notes"]
            self.counter_up = int(info["counterUp"])
            self.counter_down = int(info["counterDown"])

    def get_line_text(self):
        return "{:<25s}\t{:<6s}\t{}".format(self.text,
                                            str(self.counter_up) + "/" + str(self.counter_down),
                                            ", ".join(self.get_tag_names()))


class Daily(Task):
    def __init__(self, id, headers, retrieve_info=True, text=None, notes=None):
        Task.__init__(self, id, headers, retrieve_info, text, notes)
        self.type = "Daily"

    def get_line_text(self):
        return "{:<25s}\t{:<6s}\t{}".format(self.text, "XX/XX", ", ".join(self.get_tag_names()))


class User:
    def __init__(self, api_user, api_key, bpomo_id=None, bpomoset_id=None):
        self.headers = {
            'x-api-user': api_user,
            'x-api-key': api_key,
        }

        self.pomo_tags = dict()
        self.habits = dict()
        self.dailys = dict()
        self.basic_pomo = None
        self.basic_pomoset = None

        self.username = None
        self.hp = None
        self.max_hp = None
        self.exp = None
        self.exp_next = None
        self.lvl = None
        self.gold = None

        self.update_profile_stats()
        self.update_pomo_tags()
        self.create_tasks_from_tags()
        self.create_basic_pomo_habits(bpomo_id, bpomoset_id)

        # verbose
        self.v = True
        if self.v: print(self.get_all_text())


    def create_basic_pomo_habits(self, bpomo_id, bpomoset_id):
        if bpomo_id:
            self.basic_pomo = Habit(bpomo_id, self.headers, retrieve_info=True)

        if bpomoset_id:
            self.basic_pomoset = Habit(bpomoset_id, self.headers, retrieve_info=True)

    def get_all_tasks(self):
        r = requests.get('https://habitica.com/api/v3/tasks/user', headers=self.headers)

        result = json.loads(r.content)
        if r.ok:
            if result["success"]:
                habit_list = dict()
                daily_list = dict()
                for task in result["data"]:
                    if task["type"] == "habit":
                        new_task = Habit(task["id"], self.headers, retrieve_info=False,
                                         text=task["text"], notes=task["notes"],
                                         counter_up=int(task["counterUp"]),
                                         counter_down=int(task["counterDown"]))
                        if new_task:
                            habit_list[task["id"]] = new_task
                    elif task["type"] == "daily":
                        new_task = Daily(task["id"], self.headers, retrieve_info=False,
                                         text=task["text"], notes=task["notes"])
                        if new_task:
                            daily_list[task["id"]] = new_task
                return habit_list, daily_list
            else:
                return False
        else:
            return False

    def create_tasks_from_tags(self):
        r = requests.get('https://habitica.com/api/v3/tasks/user', headers=self.headers)

        result = json.loads(r.content)
        if r.ok:
            if result["success"]:
                for task in result["data"]:
                    if task["tags"]:
                        new_tag_list = dict()
                        for tag in task["tags"]:
                            if tag in self.pomo_tags:
                                new_tag_list[tag] = self.pomo_tags[tag]
                        if new_tag_list:
                            if task["type"] == "habit":
                                new_task = Habit(task["id"], self.headers, retrieve_info=False,
                                                 text=task["text"], notes=task["notes"],
                                                 counter_up=int(task["counterUp"]), counter_down=int(task["counterDown"]))
                                if new_task:
                                    new_task.tags = new_tag_list
                                    self.habits[task["id"]] = new_task
                            elif task["type"] == "daily":
                                new_task = Daily(task["id"], self.headers, retrieve_info=False,
                                                 text=task["text"], notes=task["notes"])
                                if new_task:
                                    new_task.tags = new_tag_list
                                    self.dailys[task["id"]] = new_task
                return True
            else:
                return False
        else:
            return False

    def update_profile_stats(self):
        r = requests.get('https://habitica.com/api/v3/user', headers=self.headers)

        result = json.loads(r.content)
        if r.ok:
            if result["success"]:
                # Profile
                self.username = result["data"]["profile"]["name"]

                # Stats
                stats = result["data"]["stats"]
                self.hp = stats["hp"]
                self.max_hp = stats["maxHealth"]
                self.exp = stats["exp"]
                self.exp_next = stats["toNextLevel"]
                self.lvl = stats["lvl"]
                self.gold = stats["gp"]
                return True
            else:
                return False
        else:
            return False

    def update_pomo_tags(self):
        r = requests.get('https://habitica.com/api/v3/tags', headers=self.headers)

        result = json.loads(r.content)
        if r.ok:
            if result["success"]:
                for tag in result["data"]:
                    if ":tomato:" in tag["name"]:
                        self.pomo_tags[tag["id"]] = tag["name"].replace(":tomato:", "")
                return True
            else:
                return False
        else:
            return False

    def update_taks(self):
        for id in self.habits:
            self.habits[id].update()
        for id in self.dailys:
            self.dailys[id].update()

    def update_basic_pomo_habits(self):
        if self.basic_pomo:
            self.basic_pomo.update()
        if self.basic_pomoset:
            self.basic_pomoset.update()

    def score_basic_pomo(self, set_interval, update_tasks=False):
        drops = list()
        if self.basic_pomo:
            p_score_result = self.basic_pomo.score()
            if self.v: print("Basic pomo scored [{}]: {}".format(self.basic_pomo.counter_up, p_score_result))
            if p_score_result:
                self.hp, self.exp, self.lvl, self.gold = p_score_result[0], p_score_result[1], p_score_result[2],\
                                                         p_score_result[3]
                if p_score_result[4]:
                    drops.append(p_score_result[4])
                if update_tasks:
                    self.basic_pomo.update()
                    if self.v: print("Basic pomo was updated: {}".format(self.basic_pomo.get_line_text()))

                # Updating Pomodoro Set
                if self.basic_pomoset and set_interval:
                    if self.basic_pomo.counter_up % set_interval == 0:
                        set_score_result = self.basic_pomoset.score()
                        if self.v: print("Pomo Set scored [{}]: {}".format(self.basic_pomoset.counter_up, set_score_result))
                        if set_score_result:
                            self.hp, self.exp, self.lvl, self.gold = set_score_result[0], set_score_result[1], \
                                                                     set_score_result[2], set_score_result[3]
                            if set_score_result[4]:
                                drops.append(p_score_result[4])
                            if update_tasks:
                                self.basic_pomoset.update()
                                if self.v: print("Pomo Set was updated: {}".format(self.basic_pomoset.get_line_text()))
        if self.v: print("Basic/Set pomo drops: {}".format(drops))
        return drops

    def score_habit(self, id, set_interval, update_tasks=False):
        drops = list()
        if self.habits[id]:
            t_score_result = self.habits[id].score()
            if self.v: print("{} scored [{}]: {}".format(self.habits[id].text, self.habits[id].counter_up, t_score_result))
            if t_score_result:
                self.hp, self.exp, self.lvl, self.gold = t_score_result[0], t_score_result[1], t_score_result[2], \
                                                         t_score_result[3]
                if t_score_result[4]:
                    drops.append(t_score_result[4])
                if update_tasks:
                    self.habits[id].update()
                    if self.v: print("{} was updated: {}".format(self.habits[id].text, self.habits[id].get_line_text()))

                # # Updating dailies
                # if daily_id:
                #     if daily_task_list:
                #         total_count = 0
                #         tasks_array = ""
                #         for task in daily_task_list:
                #             daily_name = daily_task_list[task]["daily"]
                #             count_r = get_task(daily_task_list[task]["id"])
                #             total_count += count_r["counterUp"]
                #             tasks_array += "\n\tTotal: {:02d} | {}".format(count_r["counterUp"], count_r["text"])
                #         if get_task(daily_id)["completed"]:
                #             print("'{}' is already completed".format(daily_name))
                #         else:
                #             print("Daily associated: {}".format(daily_name), end="")
                #             print(tasks_array)
                #             print("\t===============\n\tTotal: {:02d} / {:02d}".format(total_count, pomo_set_interval))
                #             if total_count >= pomo_set_interval:
                #                 d_r = score_task(daily_id, True)
                #                 if d_r:
                #                     print("Daily task '{}' was completed!".format(daily_name))
                #                 else:
                #                     print("Habitica API Error when scoring the daily")
                #
                #     else:
                #         print("Error: A list of tasks sharing the same daily was not send")

        if self.v: print("Habit/Dailys drops: {}".format(drops))
        return drops

    # For tests
    def get_all_text(self):
        text = "{} (lv{:.0f})\n".format(self.username, self.lvl)
        text += "\tHP: {:.0f} / {}\n".format(self.hp, self.max_hp)
        text += "\tExp: {:.0f} / {}\n".format(self.exp, self.exp_next)
        text += "\tGold: {:.0f}".format(self.gold)

        if self.basic_pomo:
            text += "\nBasic Pomodoros:\n"
            text += "\t{}\n".format(self.basic_pomo.get_line_text())
            text += "\t{}".format(self.basic_pomoset.get_line_text())

        text += "\nHabits:\n"
        if self.habits:
            for id in self.habits:
                text+= "\t{}\n".format(self.habits[id].get_line_text())
        else:
            text += "\tNo habits\n"

        text += "Dailys:\n"
        if self.dailys:
            for id in self.dailys:
                text += "\t{}\n".format(self.dailys[id].get_line_text())
        else:
            text += "\tNo habits\n"

        return text


def main():
    # State: 0 exit | 1 menu | 2 post-menu | 3 pomodoro | 4 break
    state = 0
    current_task = None
    task_list = dict()
    pomo_id_exists = config.has_option("HabiticaPomodoro", "PomodoroID")
    pomo_set_id_exists = config.has_option("HabiticaPomodoro", "PomodoroSetID")

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
                if pomo_id_exists:
                    r = get_task(config.get("HabiticaPomodoro", "PomodoroID"))
                    print_task_name(r, counts=True, notes=True)
                else:
                    print("Basic Pomodoro Timer")
            is_interrupted = pomodoro.timeout_input(int(config.get("Pomodoro", "TaskMinutes")), "Press Intro for stop")
            if is_interrupted:
                print("\x1b[2K\rTask was interrupted before time")
                state = 4
            else:
                if current_task:
                    # Updating basic pomodoro
                    if pomo_set_id_exists:
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
            print("break")
        else:
            print("Warning: Bad state")