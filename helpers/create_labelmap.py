import os
import logging
import xml.etree.ElementTree as ET


class LabelMap:
    def __init__(self, labelimg_path, annotation_path, LABEL_MAP_NAME, champion_names):
        self.LABELIMG_PATH = labelimg_path
        self.ANNOTATION_PATH = annotation_path
        self.LABEL_MAP_NAME = LABEL_MAP_NAME
        self.champion_names = champion_names

    # Extracts the names from all the XMLs
    def extract_names_from_xml(self):
        unique_names = set()

        for dirpath, dirnames, filenames in os.walk(self.LABELIMG_PATH):
            for filename in filenames:
                if filename.endswith(".xml"):
                    tree = ET.parse(os.path.join(dirpath, filename))
                    root = tree.getroot()

                    # Extract names and add to the set
                    for name_elem in root.findall(".//name"):
                        if name_elem.text in self.champion_names:
                            unique_names.add(name_elem.text)

        return list(unique_names)

    # Converts a list of names to a list of dicts with id and name
    def names_to_labels(self, names_list):
        return [{"name": name, "id": idx + 1} for idx, name in enumerate(names_list)]

    # Creates the label map
    def make_label_map(self):
        names_from_xmls = self.extract_names_from_xml()
        LABELMAP = os.path.join(self.ANNOTATION_PATH, self.LABEL_MAP_NAME)
        labels = self.names_to_labels(names_from_xmls)

        with open(LABELMAP, "w") as f:
            for label in labels:
                f.write("item { \n")
                f.write("\tname:'{}'\n".format(label["name"]))
                f.write("\tid:{}\n".format(label["id"]))
                f.write("}\n")
        logging.info(f"Successfully created the LABELMAP file: {LABELMAP}")
