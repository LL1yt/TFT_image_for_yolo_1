import os
import string


def main():
    ANNOTATION_PATH = os.path.join("Tensorflow", "workspace", "annotation")
    LABEL_MAP_NAME = "label_map.pbtxt"
    LABELMAP = os.path.join(ANNOTATION_PATH, LABEL_MAP_NAME)
    labels = [
    ]
    champion_names = list(string.ascii_lowercase)

    start_id = 1  # начиная с 2, так как у последнего из предыдущих элементов id = 4
    for champ in champion_names:
        labels.append({"name": champ, "id": start_id})
        start_id += 1

    print(labels)

    with open(LABELMAP, "w") as f:
        for label in labels:
            f.write("item { \n")
            f.write("\tname:'{}'\n".format(label["name"]))
            f.write("\tid:{}\n".format(label["id"]))
            f.write("}\n")


if __name__ == "__main__":
    main()

# python /home/n0name/projects/TFT/Tensorflow/models/research/object_detection/model_main_tf2.py --model_dir=Tensorflow/workspace/pretrainedmodels/centernet_resnet50_v1_fpn_512x512_coco17_tpu-8 --pipeline_config_path=Tensorflow/workspace/pretrainedmodels/centernet_resnet50_v1_fpn_512x512_coco17_tpu-8/pipeline.config --num_train_steps=2000