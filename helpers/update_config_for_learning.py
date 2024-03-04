import logging
import tensorflow as tf
from object_detection.protos import pipeline_pb2
from google.protobuf import text_format
from object_detection.utils import label_map_util


def update_config(
    PIPELINE_CONFIG="Tensorflow/workspace/models/model_for_TFT/pipeline.config",
    labels_path="Tensorflow/workspace/annotation/label_map.pbtxt",
    train_record="Tensorflow/workspace/annotation/train.record",
    test_record="Tensorflow/workspace/annotation/test.record",
):
    pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
    with tf.io.gfile.GFile(PIPELINE_CONFIG, "r") as f:
        proto_str = f.read()
        text_format.Merge(proto_str, pipeline_config)

    label_map = label_map_util.load_labelmap(labels_path)
    labels = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=90, use_display_name=True
    )
    pipeline_config.model.ssd.num_classes = len(labels)
    pipeline_config.train_config.batch_size = 32
    pipeline_config.train_config.fine_tune_checkpoint = ""
    pipeline_config.train_config.fine_tune_checkpoint_type = "detection"
    pipeline_config.train_input_reader.label_map_path = labels_path
    pipeline_config.train_input_reader.tf_record_input_reader.input_path[:] = [
        train_record
    ]
    pipeline_config.eval_input_reader[0].label_map_path = labels_path
    pipeline_config.eval_input_reader[0].tf_record_input_reader.input_path[:] = [
        test_record
    ]

    config_text = text_format.MessageToString(pipeline_config)
    with tf.io.gfile.GFile(PIPELINE_CONFIG, "wb") as f:
        f.write(config_text)
    logging.info(f"Successfully updated the PIPELINE_CONFIG file: {PIPELINE_CONFIG}")


if __name__ == "__main__":
    update_config()
