import xml.etree.ElementTree as ET
from xml.dom import minidom
import os


class XmlAnnotation:
    IMAGE_WIDTH = "1920"
    IMAGE_HEIGHT = "1080"
    IMAGE_DEPTH = "3"
    DATABASE_NAME = "Unknown"

    def __init__(self, image_path, champion_coordinates, folder):
        self.image_path = image_path
        self.champion_coordinates = champion_coordinates
        self.folder = folder

    def _create_object_element(self, champ_name, coords, parent_element):
        """Helper function to create an <object> XML element."""
        object_elem = ET.SubElement(parent_element, "object")
        ET.SubElement(object_elem, "name").text = str(champ_name)
        ET.SubElement(object_elem, "pose").text = "Unspecified"
        ET.SubElement(object_elem, "truncated").text = "0"
        ET.SubElement(object_elem, "difficult").text = "0"
        bndbox = ET.SubElement(object_elem, "bndbox")
        ET.SubElement(bndbox, "xmin").text = str(coords[0])
        ET.SubElement(bndbox, "ymin").text = str(coords[1])
        ET.SubElement(bndbox, "xmax").text = str(coords[2])
        ET.SubElement(bndbox, "ymax").text = str(coords[3])

    def modified_create_annotation_xml(self):
        annotation = ET.Element("annotation")
        last_folder_name = os.path.basename(os.path.normpath(self.folder))
        ET.SubElement(annotation, "folder").text = last_folder_name
        ET.SubElement(annotation, "filename").text = os.path.basename(self.image_path)
        ET.SubElement(annotation, "path").text = self.folder
        source = ET.SubElement(annotation, "source")
        ET.SubElement(source, "database").text = self.DATABASE_NAME
        size = ET.SubElement(annotation, "size")
        ET.SubElement(size, "width").text = self.IMAGE_WIDTH
        ET.SubElement(size, "height").text = self.IMAGE_HEIGHT
        ET.SubElement(size, "depth").text = self.IMAGE_DEPTH
        ET.SubElement(annotation, "segmented").text = "0"

        for champ_name, all_coords in self.champion_coordinates.items():
            for coords in all_coords:
                self._create_object_element(champ_name, coords, annotation)

        xmlname = os.path.splitext(os.path.basename(self.image_path))[0] + ".xml"
        xmlfullname = os.path.join(self.folder, xmlname)
        xml_str = minidom.parseString(ET.tostring(annotation)).toprettyxml(indent="  ")
        with open(xmlfullname, "w") as f:
            f.write(xml_str)
