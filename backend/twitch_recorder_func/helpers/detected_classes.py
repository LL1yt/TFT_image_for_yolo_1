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

    def check_classes_with_few_mentions(self, champion_coordinates, class_counts):
        class_counts = class_counts

        for champion in champion_coordinates:
            class_name = next(iter(champion))  # Extract class name
            if class_counts.get(class_name, 0) < 3:
                True

        False

    def all_classes_mentioned_three_times(self, class_counts):
        class_counts = class_counts

        for count in class_counts.values():
            if count < 3:
                return False
        return True

    def update_class_counts_with_coordinates(self, class_counts, champion_coordinates):
        for champion in champion_coordinates:
            class_name = next(iter(champion))  # Extract class name
            if class_name in class_counts:
                class_counts[class_name] += 1
            else:
                class_counts[class_name] = 1
        return class_counts
