import easyocr
import cv2
import numpy as np
import time
import logging
import streamlink
import re
import os
import uuid

from helpers.detected_classes import DetectedClasses
from helpers.champion_checker import ChampionChecker
from helpers.yolov9_label_creator import YOLOv9LabelCreator


def clean_and_lowercase(s):
    cleaned = re.sub("[^a-zA-Z]", "", s.strip())
    return cleaned.lower()


class VideoTextRecognition:
    def __init__(
        self,
        username,
        champion_name_coordinates_list,
        champion_card_coordinates_list,
        champion_names,
        quality,
        IMAGES_PATH,
        LABELIMG_PATH,
        second_per_frame=10,
        number_imgs=200,
    ):
        self.username = username
        self.champion_name_coordinates_list = champion_name_coordinates_list
        self.champion_card_coordinates_list = champion_card_coordinates_list
        self.champion_names = champion_names
        self.quality = quality
        self.reader = easyocr.Reader(["en"])
        self.IMAGES_PATH = IMAGES_PATH
        self.LABELIMG_PATH = LABELIMG_PATH
        self.check_test = True
        self.second_per_frame = second_per_frame
        self.number_imgs = number_imgs
        self.detected_champion_names = DetectedClasses(
            self.champion_names, self.LABELIMG_PATH
        )

        self.train_img_path = os.path.join(self.IMAGES_PATH, "train")
        self.train_label_path = os.path.join(self.LABELIMG_PATH, "train")
        self.val_img_path = os.path.join(self.IMAGES_PATH, "val")
        self.test_img_path = os.path.join(self.IMAGES_PATH, "test")

    def get_stream_url(self, user):
        try:
            strim = streamlink.streams(f"https://twitch.tv/{user}")
            url = strim[self.quality].url
            logging.info("Stream URL retrieved successfully")
            return url
        except Exception as e:
            logging.info(f"Error retrieving stream URL: {e}")
            return None

    def process_stream(self):
        logging.info("Starting stream processing")
        stream_url = self.get_stream_url(self.username)

        if not stream_url:
            return
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            logging.info(f"Error: Unable to open video stream {stream_url}.")
            return

        frame_count = 0

        fps = int(cap.get(cv2.CAP_PROP_FPS))

        while True:
            ret, frame = cap.read()
            if not ret:
                logging.info(f"Error: Unable to read frame from video stream.")
                break
            # Если текущий кадр делится на 5 секунд без остатка, сохраняем его
            if frame_count % (self.second_per_frame * fps) == 0:

                cv2.destroyAllWindows()
                cv2.imshow(stream_url, frame)
                cv2.waitKey(1)

                logging.info(f"------------------------------------------")
                logging.info(f"------------------------------------------")
                logging.info(f"Processing frame {frame_count}")
                self.process_frame(frame)
            frame_count += 1

        cap.release()
        cv2.destroyAllWindows()
        logging.info("Stream processing completed")

    def process_frame(self, frame):
        champion_coordinates = {}
        test_index = 0
        for coordinate_index, region in enumerate(self.champion_name_coordinates_list):
            x_start, y_start, x_end, y_end = region
            roi = frame[y_start:y_end, x_start:x_end]
            results = self.reader.readtext(roi)
            logging.info(f"OCR results: {results}")

            for bbox, text, prob in results:
                cv2.imshow(text, roi)
                cv2.waitKey(1)
                champ_name = clean_and_lowercase(text)
                test_index += 1
                if text in self.champion_names:
                    logging.info(
                        f"bbox: {bbox}. Champion '{text}' detected in region {region}. prob: {prob}."
                    )
                    if champ_name in champion_coordinates:
                        champion_coordinates[champ_name].append(
                            self.champion_card_coordinates_list[coordinate_index]
                        )
                    else:
                        champion_coordinates[champ_name] = [
                            self.champion_card_coordinates_list[coordinate_index]
                        ]
                    logging.info(
                        f"2) champ_name: {champ_name}; index: {coordinate_index+1}"
                    )

        self.process_champion_coordinates(champion_coordinates, frame, test_index)

    @staticmethod
    def count_files_in_directory(directory_path):
        """Count the number of files in a directory."""
        return sum(
            1
            for f in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, f))
        )

    def process_champion_coordinates(self, champion_coordinates, frame, test_index):
        """Process champion coordinates and perform necessary actions."""

        logging.info(
            f"3) screen_for_champ: {len(champion_coordinates)} test_index: {test_index}"
        )

        file_count_train = self.count_files_in_directory(self.train_img_path)
        file_count_val = self.count_files_in_directory(self.val_img_path)
        file_count_test = self.count_files_in_directory(self.test_img_path)
        file_count = file_count_train + file_count_test + file_count_val

        # Check if total number of files exceeds predefined limit

        if (
            file_count < self.number_imgs
            or ChampionChecker.is_champion_missing(
                self.detected_champion_names, champion_coordinates
            )
            or (len(self.detected_champion_names) < len(self.champion_names))
        ):

            image_id = str(uuid.uuid1())

            imgname = os.path.join(self.train_img_path, f"{image_id}.jpg")
            cv2.imwrite(imgname, frame)
            # cv2.imshow("creating data fro model", frame)
            cv2.waitKey(1)

            # Assuming that create_annotation_xml is the correct method to call based on provided context

            label_creator = YOLOv9LabelCreator(
                self.champion_names, self.train_label_path
            )
            label_creator.create_labels(image_id, champion_coordinates)

            logging.info(f"Image {image_id} saved")
            if ChampionChecker.is_champion_missing(
                self.detected_champion_names, champion_coordinates
            ):
                ChampionChecker.add_missing_champions(
                    self.detected_champion_names, champion_coordinates
                )
        else:
            logging.info(
                f"name exists in labels or total number of files in {self.IMAGES_PATH} is {file_count}"
            )
