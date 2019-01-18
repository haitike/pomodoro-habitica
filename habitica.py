import json
import requests


class Task:
    def __init__(self, id, headers, retrieve_info=True, text=None, notes=None):
        self.id = id
        self.headers = headers
        self.type = "Task"

        if retrieve_info:
            self.update()
        else:
            self.text = text
            self.notes = notes

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

class Habit(Task):
    def __init__(self, id, headers, retrieve_info=True, text=None, notes=None, counter_up=None, counter_down=None, up=None, down=None):
        Task.__init__(self, id, headers, retrieve_info, text, notes)
        self.type = "Habit"
        self.daily = None   # Daily ID String
        self.code = None    # String

        if not retrieve_info:
            self.counter_up = counter_up
            self.counter_down = counter_down
            self.up = up
            self.down = down

    def update(self):
        info = self.retrieve_from_habitica()
        if info:
            self.text = info["text"]
            self.notes = info["notes"]
            self.counter_up = int(info["counterUp"])
            self.counter_down = int(info["counterDown"])
            self.up = info["up"]
            self.down = info["down"]

class Daily(Task):
    def __init__(self, id, headers, retrieve_info=True, text=None, notes=None, completed=None):
        Task.__init__(self, id, headers, retrieve_info, text, notes)
        self.type = "Daily"
        self.habits = list()

        if not retrieve_info:
            self.completed = completed

    def update(self):
        info = self.retrieve_from_habitica()
        if info:
            self.text = info["text"]
            self.notes = info["notes"]
            self.completed = info["completed"]

class User:
    def __init__(self, verbose=False):
        self.v = verbose

        self.code = None
        self.habits = dict()
        self.dailys = dict()
        self.headers = None
        self.basic_pomo = None
        self.basic_pomoset = None

        self.username = None
        self.hp = None
        self.max_hp = None
        self.exp = None
        self.exp_next = None
        self.lvl = None
        self.gold = None

    def set_headers(self, api_user, api_key):
        self.headers = {
            'x-api-user': api_user,
            'x-api-key': api_key,
        }

    def create_basic_pomo_habits(self, bpomo_id, bpomoset_id):
        if bpomo_id:
            self.basic_pomo = Habit(bpomo_id, self.headers, retrieve_info=True)

        if bpomoset_id:
            self.basic_pomoset = Habit(bpomoset_id, self.headers, retrieve_info=True)

    def generate_dailys(self):
        for habit_id in self.habits:
            daily_id = self.habits[habit_id].daily
            if daily_id:
                if daily_id not in self.dailys:
                    self.dailys[daily_id] = Daily(daily_id, self.headers)
                self.dailys[daily_id].habits.append(habit_id)

    def update_profile(self):
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
                if self.v:
                    text = "{} (lv{:.0f})\n".format(self.username, self.lvl)
                    text += "\tHP: {:.0f} / {}\n".format(self.hp, self.max_hp)
                    text += "\tExp: {:.0f} / {}\n".format(self.exp, self.exp_next)
                    text += "\tGold: {:.0f}".format(self.gold)
                    print(text)

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

    def daily_count(self, daily_id):
        x = 0
        for h in self.dailys[daily_id].habits:
            x += self.habits[h].counter_up

        return x

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
                    if self.v: print("Basic pomo was updated!")

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
                                if self.v: print("Pomo Set was updated!")
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
                    if self.v: print("{} was updated!".format(self.habits[id].text))

                # Scoring dailys
                daily_id = self.habits[id].daily
                if daily_id and set_interval:
                    if self.dailys[daily_id].completed:
                        if self.v: print("{} was already completed. No action needed.".format(self.dailys[daily_id].text))
                    else:
                        daily_count = self.daily_count(daily_id)
                        if daily_count >= set_interval:
                            d_score_result = self.dailys[daily_id].score()
                            if self.v: print(
                                "{} scored [{}/{}]: {}".format(self.dailys[daily_id].text, self.daily_count(daily_id),
                                                               set_interval, d_score_result))
                            if d_score_result:
                                self.hp, self.exp, self.lvl, self.gold = d_score_result[0], d_score_result[1], \
                                                                         d_score_result[2], d_score_result[3]
                                if d_score_result[4]:
                                    drops.append(d_score_result[4])
                                if update_tasks:
                                    self.dailys[daily_id].update()
                                    if self.v: print("{} was updated!".format(self.dailys[daily_id].text))
        if self.v: print("Habit/Dailys drops: {}".format(drops))
        return drops

def get_tasks_order(headers):
    r = requests.get('https://habitica.com/api/v3/user?userFields=tasksOrder', headers=headers)

    result = json.loads(r.content)
    if r.ok:
        if result["success"]:
            return result["data"]["tasksOrder"]
        else:
            return False
    else:
        return False


def get_user_tasks(headers):
    r = requests.get('https://habitica.com/api/v3/tasks/user', headers=headers)

    result = json.loads(r.content)
    if r.ok:
        if result["success"]:
            habit_list = dict()
            daily_list = dict()
            for task in result["data"]:
                if task["type"] == "habit":
                    new_task = Habit(task["id"], headers, retrieve_info=False,
                                     text=task["text"], notes=task["notes"],
                                     up=task["up"], down=task["down"],
                                     counter_up=int(task["counterUp"]),
                                     counter_down=int(task["counterDown"]))
                    if new_task:
                        habit_list[task["id"]] = new_task
                elif task["type"] == "daily":
                    new_task = Daily(task["id"], headers, retrieve_info=False,
                                     text=task["text"], notes=task["notes"])
                    if new_task:
                        daily_list[task["id"]] = new_task
            return habit_list, daily_list
        else:
            return False
    else:
        return False
