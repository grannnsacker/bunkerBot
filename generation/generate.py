import random
from random import choice
import json


def generate_person():
    with open("./generation/data.json", "r", encoding='utf-8') as f:
        data = json.load(f)
        person = dict()
        person["age"] = random.randint(18, 78) # константы7?
        person["job"] = random.choice(data['job'])
        person["sex"] = random.choice(data['sex'])
        person["hobby"] = random.choice(data['hobby'])
        person["personality"] = random.choice(data['personality'])
        person["fear"] = random.choice(data['fear'])
        person["luggage"] = random.choice(data['luggage'])
        person["knowledge"] = random.choice(data['knowledge'])
        person["health"] = random.choice(data['health'])
        person["add_inf"] = random.choice(data['add_inf'])
        person["card_action"] = random.choice(data['card_action'])
        person["card_2"] = random.choice(data['card_2'])
        return person


def create_disaster():
    with open("./generation/data.json", "r", encoding='utf-8') as f:
        data = json.load(f)
        disaster = random.choice(data['disaster'])
        return disaster


def get_correct_word(number: int, param: int):
    if param == 1:
        if 11 <= number % 100 <= 14:
            return "лет"
        elif number % 10 == 1:
            return "год"
        elif 2 <= number % 10 <= 4:
            return "года"
        else:
            return "лет"
    else:
        if 11 <= number % 100 <= 14:
            return "месяцев"
        elif number % 10 == 1:
            return "месяц"
        elif 2 <= number % 10 <= 4:
            return "месяца"
        else:
            return "месяцев"


def create_shelter():
    with open("./generation/data.json", "r", encoding='utf-8') as f:
        data = json.load(f)
        shelter = dict()
        shelter["size"] = f"{50 + 50 * random.randint(0, 9)} кв. м"
        if random.randint(0, 1) % 2 == 0:
            time = random.randint(3, 6)
            shelter["time_spent"] = f"{time} {get_correct_word(time, 2)}"
        else:
            time = random.randint(1, 15)
            shelter["time_spent"] = f"{time} {get_correct_word(time, 1)}"
        shelter["condition"] = random.choice(data["condition"])
        shelter["build_reason"] = random.choice(data["build_reason"])
        shelter["location"] = random.choice(data["location"])
        shelter["room_1"] = f'{random.choice(data["room"])} ({random.choice(data["room_conditions"])})'
        tmp = random.choice(data["room"])
        while tmp == shelter["room_1"]:
            tmp = random.choice(data["room"])
        shelter["room_2"] = f'{tmp} ({random.choice(data["room_conditions"])})'
        tmp = random.choice(data["room"])
        while tmp == shelter["room_1"] or tmp == shelter["room_2"]:
            tmp = random.choice(data["room"])
        shelter["room_3"] = f'{tmp} ({random.choice(data["room_conditions"])})'
        shelter["available_resource_1"] = random.choice(data["available_resource"])
        tmp = random.choice(data["available_resource"])
        while tmp == shelter["available_resource_1"]:
            tmp = random.choice(data["available_resource"])
        shelter["available_resource_2"] = tmp
        return shelter