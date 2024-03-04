# config_loader.py

import json


def load_config():
    with open("config.json", "r") as file:
        loaded_data = json.load(file)
    return loaded_data
