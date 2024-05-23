import os
import random
import shutil


class ImageDatasetSplitter:
    def __init__(self, images_path):
        self.images_path = images_path
        self.train_img_path = os.path.join(images_path, "train")
        self.val_img_path = os.path.join(images_path, "val")
        self.test_img_path = os.path.join(images_path, "test")

    def count_files_in_directory(self, directory):
        return len(
            [
                name
                for name in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, name))
            ]
        )

    def split_dataset(self):
        all_images = [
            f
            for f in os.listdir(self.images_path)
            if os.path.isfile(os.path.join(self.images_path, f))
        ]
        random.shuffle(all_images)

        total_images = len(all_images)
        num_val = int(0.15 * total_images)
        num_test = int(0.05 * total_images)
        num_train = total_images - num_val - num_test

        train_images = all_images[:num_train]
        val_images = all_images[num_train : num_train + num_val]
        test_images = all_images[num_train + num_val :]

        self._move_files(train_images, self.train_img_path)
        self._move_files(val_images, self.val_img_path)
        self._move_files(test_images, self.test_img_path)

    def _move_files(self, files, destination):
        if not os.path.exists(destination):
            os.makedirs(destination)
        for file in files:
            shutil.move(
                os.path.join(self.images_path, file), os.path.join(destination, file)
            )
