import json
import champions_list_from_mobalytics as champ_list


# Определите вашу конфигурацию как словарь Python
# Создание словаря для хранения данных конфигурации
config_data = {
    "twitch": {
        "username": "k3soju",
        "quality": "1080p60",
        "client_id": "uyqdeb7zi3eb5yjzw9ti0ed5akks1c",
        "client_secret": "1xzzmqd0rv5lnl0hwubl8l07w4kovv",
        "url": "https://api.twitch.tv/helix/streams",
        "refresh": 15,
        "CATEGORY_ID": 513143,
    },
    "champion_name_coordinates": {
        "ccc1": {"x_start": 484, "y_start": 1044, "x_end": 633, "y_end": 1066},
        "ccc2": {"x_start": 686, "y_start": 1044, "x_end": 834, "y_end": 1066},
        "ccc3": {"x_start": 888, "y_start": 1044, "x_end": 1035, "y_end": 1066},
        "ccc4": {"x_start": 1088, "y_start": 1044, "x_end": 1237, "y_end": 1066},
        "ccc5": {"x_start": 1290, "y_start": 1044, "x_end": 1438, "y_end": 1066}
        # ... добавьте другие координаты по аналогии, если они есть
    },
    "champion_card_coordinates": {
        "ccc1": {"x_start": 484, "y_start": 943, "x_end": 668, "y_end": 1038},
        "ccc2": {"x_start": 685, "y_start": 943, "x_end": 869, "y_end": 1038},
        "ccc3": {"x_start": 886, "y_start": 943, "x_end": 1070, "y_end": 1038},
        "ccc4": {"x_start": 1088, "y_start": 943, "x_end": 1271, "y_end": 1038},
        "ccc5": {"x_start": 1289, "y_start": 943, "x_end": 1472, "y_end": 1038}
        # ... добавьте другие координаты по аналогии, если они есть
    },
    "object_detection": {
        "champion_names": ["warwick", "jinx"],
        "number_imgs": 50,
    },
    "mobalytics": {"mobalytics_link": "https://app.mobalytics.gg/tft/champions"},
}

# Сохраните словарь в файл JSON
with open("config.json", "w") as file:
    json.dump(config_data, file, indent=4)

# Загрузите данные из файла JSON
with open("config.json", "r") as file:
    loaded_data = json.load(file)

mobalytics_link = loaded_data["mobalytics"]["mobalytics_link"]

champ_list = champ_list.get_champion_links(mobalytics_link)
loaded_data["object_detection"]["champion_names"] = champ_list
# добавить в словарь список из champ_list
with open("config.json", "w") as file:
    json.dump(loaded_data, file, indent=4)
