import os
import glob
import pandas as pd
import io
import logging
import xml.etree.ElementTree as ET
import tensorflow.compat.v1 as tf
from PIL import Image
from object_detection.utils import dataset_util, label_map_util
from collections import namedtuple


class TFRecordConverter:
    def __init__(
        self, xml_dir, labels_path, output_path, image_dir=None, csv_path=None
    ):
        self.xml_dir = xml_dir
        self.labels_path = labels_path
        self.output_path = output_path
        self.image_dir = image_dir if image_dir else xml_dir
        self.csv_path = csv_path

        # Suppress TensorFlow logging
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
        self.label_map = label_map_util.load_labelmap(labels_path)
        self.labels = label_map_util.convert_label_map_to_categories(
            self.label_map, max_num_classes=90, use_display_name=True
        )
        self.category_index = label_map_util.create_category_index(self.labels)
        self.label_map_dict = {item["name"]: item["id"] for item in self.labels}

    def _class_text_to_int(self, row_label):
        if row_label not in self.label_map_dict:
            logging.info(f"Warning: Label '{row_label}' not found in label map.")
            return None  # или другое действие, в зависимости от вашего контекста
        return self.label_map_dict[row_label]

    def _split(self, df, group):
        data = namedtuple("data", ["filename", "object"])
        gb = df.groupby(group)
        return [
            data(filename, gb.get_group(x))
            for filename, x in zip(gb.groups.keys(), gb.groups)
        ]

    def _create_tf_example(self, group, path):
        with tf.gfile.GFile(
            os.path.join(path, "{}".format(group.filename)), "rb"
        ) as fid:
            encoded_jpg = fid.read()
        encoded_jpg_io = io.BytesIO(encoded_jpg)
        image = Image.open(encoded_jpg_io)
        width, height = image.size

        filename = group.filename.encode("utf8")
        image_format = b"jpg"
        xmins = []
        xmaxs = []
        ymins = []
        ymaxs = []
        classes_text = []
        classes = []

        for index, row in group.object.iterrows():
            class_id = self._class_text_to_int(row["class"])
            if class_id is not None:
                xmins.append(row["xmin"] / width)
                xmaxs.append(row["xmax"] / width)
                ymins.append(row["ymin"] / height)
                ymaxs.append(row["ymax"] / height)
                classes_text.append(row["class"].encode("utf8"))
                classes.append(self._class_text_to_int(row["class"]))

        tf_example = tf.train.Example(
            features=tf.train.Features(
                feature={
                    "image/height": dataset_util.int64_feature(height),
                    "image/width": dataset_util.int64_feature(width),
                    "image/filename": dataset_util.bytes_feature(filename),
                    "image/source_id": dataset_util.bytes_feature(filename),
                    "image/encoded": dataset_util.bytes_feature(encoded_jpg),
                    "image/format": dataset_util.bytes_feature(image_format),
                    "image/object/bbox/xmin": dataset_util.float_list_feature(xmins),
                    "image/object/bbox/xmax": dataset_util.float_list_feature(xmaxs),
                    "image/object/bbox/ymin": dataset_util.float_list_feature(ymins),
                    "image/object/bbox/ymax": dataset_util.float_list_feature(ymaxs),
                    "image/object/class/text": dataset_util.bytes_list_feature(
                        classes_text
                    ),
                    "image/object/class/label": dataset_util.int64_list_feature(
                        classes
                    ),
                }
            )
        )
        return tf_example

    def xml_to_csv(self, path):
        xml_list = []
        for xml_file in glob.glob(path + "/*.xml"):
            tree = ET.parse(os.path.join(xml_file))
            root = tree.getroot()
            for member in root.findall("object"):
                value = (
                    root.find("filename").text,
                    int(root.find("size")[0].text),
                    int(root.find("size")[1].text),
                    member[0].text,
                    int(member.find("bndbox/xmin").text),
                    int(member.find("bndbox/ymin").text),
                    int(member.find("bndbox/xmax").text),
                    int(member.find("bndbox/ymax").text),
                )
                xml_list.append(value)
        column_name = [
            "filename",
            "width",
            "height",
            "class",
            "xmin",
            "ymin",
            "xmax",
            "ymax",
        ]
        xml_df = pd.DataFrame(xml_list, columns=column_name)
        return xml_df

    def convert(self):
        writer = tf.python_io.TFRecordWriter(self.output_path)
        path = os.path.join(self.image_dir)
        examples = self.xml_to_csv(self.xml_dir)
        grouped = self._split(examples, "filename")
        for group in grouped:
            tf_example = self._create_tf_example(group, path)
            writer.write(tf_example.SerializeToString())
        writer.close()
        logging.info(f"Successfully created the TFRecord file: {self.output_path}")
        if self.csv_path:
            examples.to_csv(self.csv_path, index=None)
            logging.info(f"Successfully created the CSV file: {self.csv_path}")


# The main function logic has been integrated into the convert() method of the class.
