import json

import requests

import configparser
config = configparser.ConfigParser()
config.read("config.ini")

headers = {
    'x-api-user': config.get("HabiticaAPI", "UserID"),
    'x-api-key': config.get("HabiticaAPI", "APIKey"),
}

def score_task(task_id, positive=True):
    data = {
        'type': 'task',
    }

    if positive:
        r = requests.post('https://habitica.com/api/v3/tasks/' + task_id + '/score/up', headers=headers, data=data)
    else:
        r = requests.post('https://habitica.com/api/v3/tasks/' + task_id + '/score/down', headers=headers, data=data)

    resultado = json.loads(r.content)
    if r.ok:
        if resultado["success"]:
            return resultado["data"]
        else:
            return None
    else:
        return None


def get_task(task_id):
    r = requests.get('https://habitica.com/api/v3/tasks/' + task_id, headers=headers)

    resultado = json.loads(r.content)
    if r.ok:
        if resultado["success"]:
            return resultado["data"]
        else:
            return None
    else:
        return None


