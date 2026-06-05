# core/inference/ultralytics_detector.py

import numpy as np

from ultralytics import YOLO

from core.config.settings import TRACK_OBJ
from core.contracts.schemas import Detection

from core.inference.detector_interface import DetectorInterface


class UltralyticsDetector(DetectorInterface):
    def __init__(
        self,
        model_path,
        enable_tracking=True ):
        self.model = YOLO(model_path)
        self.enable_tracking = enable_tracking

    def detect(self, frame):
        results = self.model(frame)[0]
        detections = []
        det_array = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = self.model.names[cls]
            if ENABLE_TRACKING:
                if label != TRACK_OBJ:
                    continue

            detections.append(
                Detection(
                    label,
                    conf,
                    (
                        int(x1),
                        int(y1),
                        int(x2),
                        int(y2)
                    )
                )
            )
            det_array.append(
                [
                    x1,
                    y1,
                    x2,
                    y2,
                    conf
                ]
            )
        if len(det_array) == 0:
            det_array = np.empty((0, 5))
        else:
            det_array = np.array(det_array)
        return detections, det_array

