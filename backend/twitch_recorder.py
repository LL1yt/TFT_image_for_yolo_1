import logging
import time
import requests

# from twitch_recorder_func.stream_recorder import StreamRecorder
from twitch_recorder_func.text_recognition import VideoTextRecognition
from twitch_recorder_func.setup_logger import SetupLogger
from twitch_recorder_func.twitch_res_status import TwitchResStatus
import os
from twitch_recorder_func.config_loader import load_config
from twitch_recorder_func.folder_setup import setup_folders
from twitch_recorder_func.access_token_fetcher import fetch_access_token
from twitch_recorder_func.twitch_user_fetcher import get_users_by_category
from helpers.yolov9_config_creator import YOLOv9ConfigCreator


class TwitchRecorder:
    def __init__(self):
        self.loaded_data = load_config()
        self.quality = self.loaded_data["twitch"]["quality"]
        self.client_id = self.loaded_data["twitch"]["client_id"]
        self.client_secret = self.loaded_data["twitch"]["client_secret"]
        self.url = self.loaded_data["twitch"]["url"]
        self.refresh = self.loaded_data["twitch"]["refresh"]
        self.CATEGORY_ID = self.loaded_data["twitch"]["CATEGORY_ID"]
        # Извлечение координат в виде кортежей
        self.champion_name_coordinates = {}
        for key, coords in self.loaded_data["champion_name_coordinates"].items():
            self.champion_name_coordinates[key] = (
                coords["x_start"],
                coords["y_start"],
                coords["x_end"],
                coords["y_end"],
            )
        self.champion_name_coordinates_list = list(
            self.champion_name_coordinates.values()
        )
        self.champion_card_coordinates = {}
        for key, coords in self.loaded_data["champion_card_coordinates"].items():
            self.champion_card_coordinates[key] = (
                coords["x_start"],
                coords["y_start"],
                coords["x_end"],
                coords["y_end"],
            )
        self.champion_card_coordinates_list = list(
            self.champion_card_coordinates.values()
        )
        self.champion_names = []
        self.champion_names = self.loaded_data["object_detection"]["champion_names"]
        self.champion_names_no_1 = [name[1:] for name in self.champion_names]
        self.number_imgs = self.loaded_data["object_detection"]["number_imgs"]
        self.token_url = (
            f"https://id.twitch.tv/oauth2/token?client_id={self.client_id}"
            f"&client_secret={self.client_secret}"
            f"&grant_type=client_credentials"
        )
        self.access_token = fetch_access_token(self.token_url)
        self.IMAGES_PATH = os.path.join("train_data", "images")
        self.LABELIMG_PATH = os.path.join("train_data", "labels")
        self.config_path = os.path.join("train_data")
        self.ANNOTATION_PATH = os.path.join("train_data", "workspace", "annotation")

        self.LABEL_MAP_NAME = "label_map.pbtxt"
        self.headers = {
            "Client-ID": self.client_id,
            "Authorization": "Bearer " + self.access_token,
        }
        self.user_online = get_users_by_category(
            self.headers, self.CATEGORY_ID, self.url
        )

    def check_user(self):
        info = None
        status = TwitchResStatus.ERROR
        self.user_online = get_users_by_category(
            self.headers, self.CATEGORY_ID, self.url
        )
        try:
            r = requests.get(
                self.url + "?user_login=" + self.user_online,
                headers=self.headers,
                timeout=15,
            )
            r.raise_for_status()
            info = r.json()

            if info is None or not info["data"]:
                status = TwitchResStatus.OFFLINE
            else:
                status = TwitchResStatus.ONLINE
        except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchResStatus.UNAUTH
                if e.response.status_code == 404:
                    status = TwitchResStatus.NOT_F
        return status, info

    def loop_check(self):
        while True:
            status, info = self.check_user()
            if status == TwitchResStatus.NOT_F:
                logging.error("username not found, invalid username or typo")
                time.sleep(float(self.refresh))
            elif status == TwitchResStatus.ERROR:
                logging.error("unexpected error. will try again in 5 minutes")
                time.sleep(300)
            elif status == TwitchResStatus.OFFLINE:
                logging.info(
                    "%s currently offline, checking again in %s seconds",
                    self.user_online,
                    self.refresh,
                )
                time.sleep(float(self.refresh))
            elif status == TwitchResStatus.UNAUTH:
                logging.info("unauthorized, will attempt to log back in immediately")
                self.access_token = self.fetch_access_token()
            elif status == TwitchResStatus.ONLINE:
                logging.info("%s online, stream recording in session", self.user_online)
                text_recognition = VideoTextRecognition(
                    self.user_online,
                    self.champion_name_coordinates_list,
                    self.champion_names,
                    self.quality,
                    self.IMAGES_PATH,
                    self.LABELIMG_PATH,
                )
                text_recognition.process_stream()

                logging.info("processing is done, going back to checking...")
                time.sleep(float(self.refresh))

    def run(self):
        # Настройка обработчика логов, чтобы записывать сообщения в файл
        SetupLogger().setup_logger()
        logging.info(
            "checking for %s every %s seconds, recording with %s quality",
            self.user_online,
            self.refresh,
            self.quality,
        )
        # setup_folders(self.IMAGES_PATH, self.LABELIMG_PATH, self.champion_names_no_1)
        config_creator = YOLOv9ConfigCreator(self.champion_names, self.IMAGES_PATH)
        config_creator.create_config(self.config_path)
        self.loop_check()


recorder = TwitchRecorder()


recorder.run()


# При желании вы можете использовать оставшуюся часть кода для настройки параметров и запуска записи.
