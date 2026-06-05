import cv2
import numpy as np
import onnxruntime as ort
from core.contracts.schemas import Detection
from core.config.settings import *
import time
from core.inference.detector_interface import DetectorInterface

class ONNXDetector(DetectorInterface):
    def __init__(self, 
                 model_path="core/models/yolov8n_320.onnx",
                 conf_threshold=0.5):
        self.conf_threshold = conf_threshold
        self.session = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        self.class_names = [
            "person","bicycle","car","motorcycle","airplane",
            "bus","train","truck","boat","traffic light",
            "fire hydrant","stop sign","parking meter","bench",
            "bird","cat","dog","horse","sheep","cow",
            "elephant","bear","zebra","giraffe","backpack",
            "umbrella","handbag","tie","suitcase","frisbee",
            "skis","snowboard","sports ball","kite",
            "baseball bat","baseball glove","skateboard",
            "surfboard","tennis racket","bottle","wine glass",
            "cup","fork","knife","spoon","bowl","banana",
            "apple","sandwich","orange","broccoli","carrot",
            "hot dog","pizza","donut","cake","chair","couch",
            "potted plant","bed","dining table","toilet","tv",
            "laptop","mouse","remote","keyboard","cell phone",
            "microwave","oven","toaster","sink",
            "refrigerator","book","clock","vase","scissors",
            "teddy bear","hair drier","toothbrush"
        ]

    def infer(self, frame):
        img = cv2.resize(frame, (640, 640))
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        outputs = self.session.run(
            None,
            {self.input_name: img}
        )
        return outputs

    def detect(self, frame):
        original_h, original_w = frame.shape[:2]
        self.input_width = 320
        self.input_height = 320
        #
        # Preprocess
        #
        #t0 = time.monotonic()
        img = cv2.resize(frame, (320, 320))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        #t1 = time.monotonic()
        #
        # ONNX inference
        #
        outputs = self.session.run(
            None,
            {self.input_name: img}
        )
        #t2 = time.monotonic()
        #
        # YOLOv8 ONNX output
        # (1,84,8400) -> (8400,84)
        #
        pred = outputs[0][0].T
        #t3 = time.monotonic()
        #print(
        #    f"PRE={(t1-t0)*1000:.1f} "
        #    f"INF={(t2-t1)*1000:.1f} "
        #    f"POST={(t3-t2)*1000:.1f}"
        #)
        scale_x = original_w / self.input_width
        scale_y = original_h / self.input_height
        boxes = []
        scores = []
        class_ids = []
        #
        # Confidence filtering
        #
        for row in pred:
            x, y, w, h = row[:4]
            scores_all = row[4:]
            cls = np.argmax(scores_all)
            conf = float(scores_all[cls])
            if conf < self.conf_threshold:
                continue
            x1 = int((x - w / 2) * scale_x)
            y1 = int((y - h / 2) * scale_y)
            x2 = int((x + w / 2) * scale_x)
            y2 = int((y + h / 2) * scale_y)
            boxes.append([
                x1,
                y1,
                x2 - x1,
                y2 - y1
            ])
            scores.append(conf)
            class_ids.append(cls)
        #
        # NMS
        #
        indices = cv2.dnn.NMSBoxes(
            boxes,
            scores,
            self.conf_threshold,
            0.45
        )
        detections = []
        det_array = []
        if len(indices) > 0:
            for idx in indices.flatten():
                x, y, w, h = boxes[idx]
                x1 = int(x)
                y1 = int(y)
                x2 = int(x + w)
                y2 = int(y + h)
                conf = float(scores[idx])
                cls = class_ids[idx]
                label = self.class_names[cls]
                if ENABLE_TRACKING:
                    if label != TRACK_OBJ:
                        continue
                detections.append(
                    Detection(
                        label,
                        conf,
                        (x1, y1, x2, y2)
                    )
                )
                det_array.append([
                    x1,
                    y1,
                    x2,
                    y2,
                    conf
                ])
        #
        # Maintain compatibility with tracker
        #
        if len(det_array) == 0:
            det_array = np.empty((0, 5))
        else:
            det_array = np.array(
                det_array,
                dtype=np.float32
            )
        return detections, det_array

