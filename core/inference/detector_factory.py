# core/inference/detector_factory.py

from core.config.settings import DETECTOR_TYPE

from core.inference.onnx_detector import ONNXDetector
from core.inference.ultralytics_detector import UltralyticsDetector


class DetectorFactory:

    @staticmethod
    def create(enable_tracking=True):
        if DETECTOR_TYPE == "onnx":
            return ONNXDetector()
        if DETECTOR_TYPE == "ultralytics":
            return UltralyticsDetector(
                model_path="yolov8n.pt",
                enable_tracking=enable_tracking
            )
        raise ValueError(
            f"Unknown detector type: "
            f"{DETECTOR_TYPE}"
        )

