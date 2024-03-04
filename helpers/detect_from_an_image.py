import os
import glob
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
from object_detection.utils import config_util
import cv2
import numpy as np


@tf.function
def detect_fn(image, detection_model):
    image, shapes = detection_model.preprocess(image)
    prediction_dict = detection_model.predict(image, shapes)
    detections = detection_model.postprocess(prediction_dict, shapes)
    return detections


def get_latest_ckpt_file(directory, patern="ckpt-*.index", index=0):
    # Get all files matching the pattern
    files = glob.glob(os.path.join(directory, patern))
    if not files:
        raise FileNotFoundError(
            f"No files matching the pattern '{patern}' found in the directory '{directory}'"
        )

    # Sort files by creation time
    files.sort(key=os.path.getctime, reverse=True)

    # Return the latest file
    print(
        f"Files matching the pattern '{files[index]}' found in the directory '{directory}'"
    )
    return files[index]


def display_detection_results(image, detections, category_index):
    image_np_with_detections = image.copy()
    viz_utils.visualize_boxes_and_labels_on_image_array(
        image_np_with_detections,
        detections["detection_boxes"],
        detections["detection_classes"] + 1,
        detections["detection_scores"],
        category_index,
        use_normalized_coordinates=True,
        max_boxes_to_draw=5,
        min_score_thresh=0.008,
        agnostic_mode=False,
    )

    return image_np_with_detections


def detecting(
    PIPELINE_CONFIG="Tensorflow/workspace/models/model_for_TFT/pipeline.config",
    CHECKPOINT_PATH="Tensorflow/workspace/models/model_for_TFT/",
    labels_path="Tensorflow/workspace/annotation/label_map.pbtxt",
    test_image_dir="Tensorflow/labelimg/test",
):
    # Load pipeline config and build a detection model
    configs = config_util.get_configs_from_pipeline_file(PIPELINE_CONFIG)
    detection_model = model_builder.build(
        model_config=configs["model"], is_training=False
    )

    # Restore checkpoint
    ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
    latest_file = get_latest_ckpt_file(CHECKPOINT_PATH)
    ckpt.restore(latest_file).expect_partial()

    category_index = label_map_util.create_category_index_from_labelmap(labels_path)

    latest_IMAGE_PATH_test = "Tensorflow/labelimg/test/0fb99f5c-410f-11ee-a2c7-a7fbcabc69c4.jpg"  # get_latest_ckpt_file(
    # test_image_dir, patern="*.jpg", index=7
    # )

    img = cv2.imread(latest_IMAGE_PATH_test)

    resized_image = cv2.resize(img, (640, 360))
    image_np = np.array(resized_image)

    input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
    detections = detect_fn(input_tensor, detection_model)

    num_detections = int(detections.pop("num_detections"))
    detections = {
        key: value[0, :num_detections].numpy() for key, value in detections.items()
    }
    detections["num_detections"] = num_detections

    # detection_classes should be ints.
    detections["detection_classes"] = detections["detection_classes"].astype(np.int64)

    # Display detection results on the image
    image_np_with_detections = display_detection_results(
        image_np, detections, category_index
    )

    # Получите boxes, scores и classes
    boxes = detections["detection_boxes"]
    scores = detections["detection_scores"]
    classes = detections["detection_classes"]

    confidence_threshold = 0.001

    for i in range(len(scores)):
        if scores[i] > confidence_threshold:
            print(f"Box: {boxes[i]}, Score: {scores[i]}, Class: {classes[i]}")

    cv2.imshow("Detected Image", image_np_with_detections)
    cv2.waitKey(0)  # This will display the window indefinitely until a keypress
    cv2.destroyAllWindows()


if __name__ == "__main__":
    detecting()
