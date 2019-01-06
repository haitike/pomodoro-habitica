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
            self.update_info()
        else:
            self.text = text
            self.notes = notes

    def get_tag_names(self):
        tag_names = list()
        for tag_id in self.tags:
            tag_names.append(self.tags[tag_id])
        return tag_names

    def get_info_from_habitica(self):
        r = requests.get('https://habitica.com/api/v3/tasks/' + self.id, headers=self.headers)

        result = json.loads(r.content)
        if r.ok:
            if result["success"]:
                return result["data"]
            else:
                return False
        else:
            return False

    def update_info(self):
        info = self.get_info_from_habitica()
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
                return result["data"]["hp"], result["data"]["exp"], result["data"]["lvl"]
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
        self.key_code = None
        self.notes, self.key_code = self.extract_key_code(notes)

        if not retrieve_info:
            self.counter_up = counter_up
            self.counter_down = counter_down

    def update_info(self):
        info = self.get_info_from_habitica()
        if info:
            self.text = info["text"]
            self.notes, self.key_code = self.extract_key_code(info["notes"])
            self.counter_up = info["counterUp"]
            self.counter_down = info["counterDown"]

    def get_line_text(self):
        return "{:<25s}\t{:<6s}\t{}".format(self.text,
                                            str(self.counter_up) + "/" + str(self.counter_down),
                                            ", ".join(self.get_tag_names()))

    def extract_key_code(self,text):
        new_text = ""
        key_code = None
        for line in text.splitlines():
            if line:
                if line.startswith("[//]: # ("):
                    key_code = line.replace(")", "(").split("(")[1]
                else:
                    new_text += line + "\n"
        return new_text, key_code


class Daily(Task):
    def __init__(self, id, headers, retrieve_info=True, text=None, notes=None):
        Task.__init__(self, id, headers, retrieve_info, text, notes)
        self.type = "Daily"

    def get_line_text(self):
        return "{:<25s}\t{:<6s}\t{}".format(self.text, "XX/XX", ", ".join(self.get_tag_names()))


class User:
    def __init__(self, api_user, api_key):
        self.headers = {
            'x-api-user': api_user,
            'x-api-key': api_key,
        }

        self.pomo_tags = dict()
        self.habits = list()
        self.dailys = list()

        self.username = None
        self.hp = None
        self.max_hp = None
        self.exp = None
        self.exp_next = None
        self.lvl = None
        self.gold = None

        self.update_pomo_tags()
        self.update_tasks()
        self.update_profile_stats()

    def add_habit(self, habit):
        self.habits.append(habit)

    def add_daily(self, daily):
        self.dailys.append(daily)

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

    def update_tasks(self):
        r = requests.get('https://habitica.com/api/v3/tasks/user', headers=self.headers)

        result = json.loads(r.content)
        if r.ok:
            if result["success"]:
                habit_list = list()
                daily_list = list()
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
                                                 counter_up=task["counterUp"], counter_down=task["counterDown"])
                                new_task.tags = new_tag_list
                                habit_list.append(new_task)
                            elif task["type"] == "daily":
                                new_task = Daily(task["id"], self.headers, retrieve_info=False,
                                                 text=task["text"], notes=task["notes"])
                                new_task.tags = new_tag_list
                                daily_list.append(new_task)
                self.habits = habit_list
                self.dailys = daily_list
                return True
            else:
                return False
        else:
            return False

    def score_task(self, id):
        pass

    def get_stats_text(self, tab_format=True):
        t = ""
        if tab_format: t = "\t"
        text = "{} (lv{:.0f})\n".format(self.username, self.lvl)
        text += "{}HP: {:.0f} / {}\n".format(t, self.hp, self.max_hp)
        text += "{}Exp: {:.0f} / {}\n".format(t, self.exp, self.exp_next)
        text += "{}Gold: {:.0f}".format(t, self.gold)
        return text

    def get_all_text(self):
        text = self.get_stats_text()

        text += "\nHabits:\n"
        if self.habits:
            for task in self.habits:
                text+= "\t{}\n".format(task.get_line_text())
        else:
            text += "\tNo habits\n"

        text += "Dailys:\n"
        if self.dailys:
            for task in self.dailys:
                text += "\t{}\n".format(task.get_line_text())
        else:
            text += "\tNo habits\n"

        return text


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