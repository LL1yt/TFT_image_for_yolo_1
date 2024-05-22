import easyocr
import cv2
import numpy as np
import time
import logging
import streamlink
import re


def clean_and_lowercase(s):
    s.strip()
    # Удаление всех небуквенных знаков
    cleaned = re.sub("[^a-zA-Z]", "", s)
    # Приведение к прописному регистру
    return cleaned.lower()


class VideoTextRecognition:
    def __init__(
        self, username, champion_name_coordinates_list, champion_names, quality
    ):
        self.username = username
        self.champion_name_coordinates_list = champion_name_coordinates_list
        self.champion_names = champion_names
        self.quality = quality
        self.reader = easyocr.Reader(["en"])

    def get_stream_url(self, user):
        strim = streamlink.streams("https://twitch.tv/%s" % user)
        url = strim[self.quality].url
        logging.info("get_stream_url")
        return url

    def process_stream(self):
        logging.info("record_stream begin")
        stream_url = self.get_stream_url(self.username)
        logging.info("stream_url: {stream_url}")
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            logging.info(f"Error: Unable to open video stream {stream_url}.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                logging.info(f"Error: Unable to read frame from video stream.")
                break

            cv2.destroyAllWindows()
            cv2.imshow(stream_url, frame)
            cv2.waitKey(1)

            logging.info(f"------------------------------------------")
            logging.info(f"------------------------------------------")
            self.process_frame(frame)

            time.sleep(1)  # Wait for 1 second before processing the next frame
        cap.release()
        cv2.destroyAllWindows()

    def process_frame(self, frame):
        for coordinate_index, region in enumerate(self.champion_name_coordinates_list):
            x_start, y_start, x_end, y_end = region
            roi = frame[y_start:y_end, x_start:x_end]
            results = self.reader.readtext(roi)
            logging.info(f"===================={results}====================")

            for bbox, text, prob in results:
                cv2.imshow(text, roi)
                cv2.waitKey(1)
                text = clean_and_lowercase(text)
                if text in self.champion_names:
                    logging.info(
                        f"bbox: {bbox}. Champion '{text}' detected in region {region}. prob: {prob}."
                    )
