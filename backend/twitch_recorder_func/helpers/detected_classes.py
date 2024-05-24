import os


class DetectedClasses:
    def __init__(self, champion_names, labels_path):
        self.champion_names = champion_names
        self.labels_path = labels_path

    def get_detected_classes(self):
        detected_classes = set()

        subdirectories = ["train", "test", "val"]

        for subdirectory in subdirectories:
            subdirectory_path = os.path.join(self.labels_path, subdirectory)
            for label_file in os.listdir(subdirectory_path):
                if label_file.endswith(".txt"):
                    with open(os.path.join(subdirectory_path, label_file), "r") as file:
                        for line in file:
                            parts = line.strip().split()
                            class_id = int(parts[0])
                            class_name = self.champion_names[class_id]
                            detected_classes.add(class_name)

        return list(detected_classes)

    def count_class_mentions(self):
        class_counts = {name: 0 for name in self.champion_names}

        subdirectories = ["train", "test", "val"]

        for subdirectory in subdirectories:
            subdirectory_path = os.path.join(self.labels_path, subdirectory)
            for label_file in os.listdir(subdirectory_path):
                if label_file.endswith(".txt"):
                    with open(os.path.join(subdirectory_path, label_file), "r") as file:
                        for line in file:
                            parts = line.strip().split()
                            class_id = int(parts[0])
                            class_name = self.champion_names[class_id]
                            class_counts[class_name] += 1

        return class_counts
