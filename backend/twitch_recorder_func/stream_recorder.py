import cv2
import streamlink
import logging
import pytesseract
import os
import re
import uuid
import datetime
import subprocess
import sys
import pandas as pd
import threading
import time
from sshkeyboard import listen_keyboard
from helpers.modified_create_annotation_xml import XmlAnnotation
from helpers.create_labelmap import LabelMap
from helpers.tf_record_converter import TFRecordConverter
from helpers.update_config_for_learning import update_config
from pynput import keyboard
from helpers.detect_from_an_image import detecting
from object_detection.utils import label_map_util


class StreamRecorder:
    def __init__(
        self,
        username,
        champion_name_coordinates_list,
        champion_card_coordinates_list,
        quality,
        IMAGES_PATH,
        LABELIMG_PATH,
        ANNOTATION_PATH,
        LABEL_MAP_NAME,
        champion_names,
        champion_names_no_first_letter,
        number_imgs,
        second_per_frame=5,
    ):
        self.username = username
        self.champion_name_coordinates_list = champion_name_coordinates_list
        self.champion_card_coordinates_list = champion_card_coordinates_list
        self.quality = quality
        self.IMAGES_PATH = IMAGES_PATH
        self.LABELIMG_PATH = LABELIMG_PATH
        self.ANNOTATION_PATH = ANNOTATION_PATH
        self.LABEL_MAP_NAME = LABEL_MAP_NAME
        self.champion_names = champion_names
        self.champion_names_no_first_letter = champion_names_no_first_letter
        self.number_imgs = number_imgs
        self.check_test = True
        self.second_per_frame = second_per_frame
        self.should_continue_task = True
        self.region_path = "Tensorflow/labelimg/champ_mini/"

    def get_stream_url(self, user):
        strim = streamlink.streams("https://twitch.tv/%s" % user)
        url = strim[self.quality].url
        logging.info("get_stream_url")
        return url

    def record_stream(self):
        logging.info("record_stream begin")
        # Connect to Twitch API
        stream_url = self.get_stream_url(self.username)

        # Create a VideoCapture object to read the stream
        cap = cv2.VideoCapture(stream_url)

        frame_count = 0

        # Process the video stream using cv2
        while cap.isOpened():
            if not self.should_continue_task:
                logging.info(f"Task was stopped.")
                sys.exit()
            ret, frame = cap.read()
            if ret:
                fps = int(cap.get(cv2.CAP_PROP_FPS))

                # Если текущий кадр делится на 5 секунд без остатка, сохраняем его
                if frame_count % (self.second_per_frame * fps) == 0:
                    # Обрезаем изображение с использованием заданных координат
                    cv2.destroyAllWindows()

                    champion_coordinates = {}
                    test_index = 0
                    logging.info(f"------------------------------------------")
                    logging.info(f"------------------------------------------")

                    for coordinate_index, region in enumerate(
                        self.champion_name_coordinates_list
                    ):
                        x_start, y_start, x_end, y_end = region

                        cropped_frame = frame[y_start:y_end, x_start:x_end]
                        # Получение размеров оригинального изображения
                        height, width = cropped_frame.shape[:2]

                        # Увеличение изображения в 3 раза
                        resized_frame = cv2.resize(
                            cropped_frame, (width * 3, height * 3)
                        )
                        # Преобразование в оттенки серого
                        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

                        ret, imgthresh = cv2.threshold(
                            gray_frame, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                        )
                        result = cv2.GaussianBlur(imgthresh, (5, 5), 0)
                        result = 255 - result

                        champ_name = pytesseract.image_to_string(
                            result, lang="eng", config="--psm 7"
                        )

                        logging.info(
                            f"===================={champ_name.strip()}===================="
                        )
                        logging.info(
                            f"1) pytesseract champ_name: {champ_name.strip()} index: {coordinate_index+1}"
                        )
                        # Проверка, является ли переменная text строкой
                        if not isinstance(champ_name, str):
                            champ_name = str(champ_name)
                        cv2.imshow(champ_name, result)
                        cv2.waitKey(1)
                        # Проверка на пустую строку
                        if champ_name.strip():
                            test_index += 1
                            # Преобразование всех символов строки в прописные
                            champ_name = champ_name.lower()
                            # Удаление всех символов, кроме букв
                            champ_name = re.sub(r"[^a-z]", "", champ_name)
                            # Check if the image of a champion exists based on its name.

                            if self.image_exists(champ_name):
                                champion_image = self.load_champion_image(champ_name)
                                similarity = self.get_image_similarity(
                                    champion_image, frame, coordinate_index
                                )
                                logging.info(
                                    f"Similarity between images: {similarity:.2f}%"
                                )

                            # if similarity > 70:
                            champ_name_no_first_letter = champ_name[1:]
                            # Проверка наличия текста в списке
                            if (
                                champ_name_no_first_letter
                                in self.champion_names_no_first_letter
                            ):
                                if not self.image_exists(champ_name):
                                    self.record_champ_mini(
                                        frame, coordinate_index, champ_name, frame_count
                                    )
                                if champ_name in champion_coordinates:
                                    champion_coordinates[champ_name].append(
                                        self.champion_card_coordinates_list[
                                            coordinate_index
                                        ]
                                    )
                                else:
                                    champion_coordinates[champ_name] = [
                                        self.champion_card_coordinates_list[
                                            coordinate_index
                                        ]
                                    ]
                                logging.info(
                                    f"2) champ_name: {champ_name}; index: {coordinate_index+1}"
                                )

                        logging.info(
                            f"===================={champ_name}===================="
                        )
                    # Уменьшение изображения в 3 раза
                    small_frame = cv2.resize(
                        frame, (frame.shape[1] // 2, frame.shape[0] // 2)
                    )
                    cv2.imshow("screen", small_frame)
                    cv2.waitKey(1)
                    self.process_champion_coordinates(
                        champion_coordinates, frame, test_index
                    )

                frame_count += 1

            else:
                logging.info("Не удалось получить кадр. Проверьте состояние потока.")
                break

        cap.release()
        cv2.destroyAllWindows()

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

        train_img_path = os.path.join(self.IMAGES_PATH, "train")
        test_img_path = os.path.join(self.IMAGES_PATH, "test")

        file_count_train = self.count_files_in_directory(train_img_path) / 2
        file_count_test = self.count_files_in_directory(test_img_path) / 2

        # Check if total number of files exceeds predefined limit
        label_map_path = os.path.join(self.ANNOTATION_PATH, "label_map.pbtxt")
        label_map_c = self.labels_from_labelmap(label_map_path)
        if len(label_map_c) < 58:
            if not champion_coordinates:
                logging.info(f"no champion_coordinates")
                return
            if file_count_train % 10 == 0 and self.check_test:
                labelimg_path = test_img_path
                logging.info(
                    f"TEST. number of files in {test_img_path} is {file_count_test}"
                )
                self.check_test = False
                self.second_per_frame = 10
            else:
                labelimg_path = train_img_path
                self.check_test = True
                self.second_per_frame = 15

            imgname = os.path.join(labelimg_path, f"{str(uuid.uuid1())}.jpg")
            if (
                file_count_train + file_count_test < self.number_imgs
            ) or self.class_name_not_exists(label_map_c, champion_coordinates):
                cv2.imwrite(imgname, frame)
                # cv2.imshow("creating data fro model", frame)
                cv2.waitKey(1)

                # Assuming that create_annotation_xml is the correct method to call based on provided context
                XmlAnnotation(
                    imgname, champion_coordinates, labelimg_path
                ).modified_create_annotation_xml()

                logging.info(f"{os.path.splitext(os.path.basename(imgname))[0]} saved")

                logging.info(f"creating labelmap")
                label_map = LabelMap(
                    self.LABELIMG_PATH,
                    self.ANNOTATION_PATH,
                    self.LABEL_MAP_NAME,
                    self.champion_names,
                )
                label_map.make_label_map()
            else:
                logging.info(f"name exists in labels")
        else:
            logging.info(
                f"total number of files in {self.IMAGES_PATH} is {file_count_train + file_count_test}"
            )
            logging.info(f"creating labelmap")
            label_map = LabelMap(
                self.LABELIMG_PATH,
                self.ANNOTATION_PATH,
                self.LABEL_MAP_NAME,
                self.champion_names,
            )
            label_map.make_label_map()
            tf_record_converter = TFRecordConverter(
                train_img_path,
                os.path.join(self.ANNOTATION_PATH, "label_map.pbtxt"),
                os.path.join(self.ANNOTATION_PATH, "train.record"),
            )
            tf_record_converter.convert()
            tf_record_converter.xml_dir = test_img_path
            tf_record_converter.image_dir = test_img_path
            tf_record_converter.output_path = os.path.join(
                self.ANNOTATION_PATH, "test.record"
            )
            tf_record_converter.convert()
            update_config()
            # Запуск model_main_tf2.py
            args = [  # "python", "Tensorflow/models/research/object_detection/model_main_tf2.py",
                "python",
                "Tensorflow/models/research/object_detection/model_main_tf2.py",
                "--pipeline_config_path=Tensorflow/workspace/models/model_for_TFT/pipeline.config",
                "--model_dir=Tensorflow/workspace/models/model_for_TFT",
                "--alsologtostderr",
            ]
            process = subprocess.Popen(args)

            # Если TensorBoard не запущен, запустить его
            if not self.is_tensorboard_running():
                tensorboard_args = [
                    "tensorboard",
                    "--logdir=Tensorflow/workspace/models/model_for_TFT/train",
                ]
                subprocess.Popen(tensorboard_args)
            # Ожидание завершения model_main_tf2.py
            process.wait()
            detecting()

    def time_now(self):
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        return current_time

    def is_tensorboard_running(self):
        try:
            output = subprocess.check_output(["pgrep", "-f", "tensorboard"])
            return bool(output) and "grep" not in output.decode("utf-8")
        except subprocess.CalledProcessError:
            return False

    def on_key_release(self, key):
        """Function to be called when a key is released."""
        if key == keyboard.Key.esc:
            logging.info(f"Stopping the task...")
            self.should_continue_task = False
            # Stop listener
            return False

    def start_task(self):
        """Starts the long_running_task and keyboard listener."""
        task_thread = threading.Thread(target=self.record_stream)
        task_thread.start()

        with keyboard.Listener(on_release=self.on_key_release) as listener:
            listener.join()

        task_thread.join()

    def record_champ_mini(self, frame, index, champ_name, frame_count):
        logging.info("record_champ_mini")
        (
            x_start_card,
            y_start_card,
            x_end_card,
            y_end_card,
        ) = self.champion_card_coordinates_list[index]
        cropped_frame_card = frame[y_start_card:y_end_card, x_start_card:x_end_card]
        imgname_mini = os.path.join(
            self.region_path,
            champ_name + ".jpg",
        )
        cv2.imwrite(imgname_mini, cropped_frame_card)
        cv2.imshow(champ_name, cropped_frame_card)
        cv2.waitKey(1)
        logging.info(f"Champ from frame {frame_count}: {champ_name}")

    def load_champion_image(self, champion_name):
        image_path = f"{self.region_path}/{champion_name}.jpg"  # Assuming images are in jpg format
        return cv2.imread(image_path, cv2.IMREAD_COLOR)

    def get_image_similarity(self, image1, frame, index):
        (
            x_start_card,
            y_start_card,
            x_end_card,
            y_end_card,
        ) = self.champion_card_coordinates_list[index]
        cropped_frame_card = frame[y_start_card:y_end_card, x_start_card:x_end_card]
        # Convert images to grayscale
        image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        image2_gray = cv2.cvtColor(cropped_frame_card, cv2.COLOR_BGR2GRAY)

        hist1 = self.compute_histogram(image1_gray)
        hist2 = self.compute_histogram(image2_gray)

        # Compute the Structural Similarity Index (SSI)
        ssi = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

        # Convert correlation coefficient to percentage
        similarity_percentage = ((ssi + 1) / 2) * 100

        # Convert SSI to percentage
        return similarity_percentage

    def compute_histogram(self, image, bins=256):
        hist = cv2.calcHist([image], [0], None, [bins], [0, 256])
        cv2.normalize(hist, hist)
        return hist

    def image_exists(self, champion_name):
        image_path = f"{self.region_path}/{champion_name}.jpg"  # Assuming images are in jpg format
        return os.path.exists(image_path)

    def labels_from_labelmap(self, labels_path):
        label_map = label_map_util.load_labelmap(labels_path)
        labels = label_map_util.convert_label_map_to_categories(
            label_map, max_num_classes=90, use_display_name=True
        )
        return labels

    def class_name_not_exists(self, labels, champion_coordinates):
        """
        Check if any of the class names in champion_coordinates exist in labels.

        Args:
        - labels (list): List of labels containing dictionaries with 'id' and 'name'.
        - champion_coordinates (dict): Dictionary with class names as keys.

        Returns:
        - bool: True if any class name is missing in labels, False otherwise.
        """
        return any(
            not any(category["name"] == name for category in labels)
            for name in champion_coordinates
        )
