import os


class YOLOv9LabelCreator:
    def __init__(self, champion_names, images_path):
        self.champion_names = champion_names
        self.images_path = images_path

        self.image_width = "1920"
        self.image_height = "1080"

    def convert_bbox_to_yolo_format(self, x_min, y_min, x_max, y_max):
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        width = x_max - x_min
        height = y_max - y_min

        x_center_norm = x_center / self.image_width
        y_center_norm = y_center / self.image_height
        width_norm = width / self.image_width
        height_norm = height / self.image_height

        return x_center_norm, y_center_norm, width_norm, height_norm

    def create_labels(self, image_id, objects):
        label_path = os.path.join(self.images_path, f"{image_id}.txt")

        with open(label_path, "w") as label_file:
            for champ_name, bbox_list in objects.items():
                class_id = self.champion_names.index(champ_name)
                for bbox in bbox_list:
                    x_min, y_min, x_max, y_max = bbox
                    x_center_norm, y_center_norm, width_norm, height_norm = (
                        self.convert_bbox_to_yolo_format(x_min, y_min, x_max, y_max)
                    )
                    label_file.write(
                        f"{class_id} {x_center_norm} {y_center_norm} {width_norm} {height_norm}\n"
                    )
        print(f"Label file created: {label_path}")
