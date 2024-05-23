import os
import yaml


class YOLOv9ConfigCreator:
    def __init__(self, champion_names, images_path):
        self.champion_names = champion_names
        self.train_img_path = os.path.join(images_path, "train")
        self.val_img_path = os.path.join(images_path, "val")
        self.test_img_path = os.path.join(images_path, "test")

    def create_config(self, config_path):
        config = {
            "path": config_path,  # class names
            "train": self.train_img_path,
            "val": self.val_img_path,
            "test": self.test_img_path,
            "nc": len(self.champion_names),
            "names": self.champion_names,
        }

        with open(config_path, "w") as file:
            yaml.dump(config, file, default_flow_style=False)
        print(f"Configuration file saved to {config_path}")
