import os


class DetectedClasses:
    def __init__(self, champion_names, labels_path):
        self.champion_names = champion_names
        self.labels_path = os.path.join(labels_path, "train")

    def get_detected_classes(self):
        detected_classes = set()

        for label_file in self.labels_path:
            if label_file.endswith(".txt"):
                with open(os.path.join(self.labels_path, label_file), "r") as file:
                    for line in file:
                        parts = line.strip().split()
                        class_id = int(parts[0])
                        class_name = self.champion_names[class_id]
                        detected_classes.add(class_name)

        return list(detected_classes)
