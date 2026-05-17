# core/inference/inference_service.py

from core.config.settings import *
from core.app.service import BaseService
import time
import threading
#from core.messaging.shm_bus import SharedMemoryBus
from core.contracts.schemas import Detection, Result, TrackedObject
from ultralytics import YOLO
from core.config.settings import *
import numpy as np


class InferenceService(BaseService):
    def __init__(self, fbus, rbus, w=FRAME_Y, h=FRAME_X):
        super().__init__("InferenceService")
        self.frame_bus = fbus
        self.result_bus = rbus
        self.model = YOLO("models/yolov8n.pt")  # YOLO load
        self.enable_tracking = ENABLE_TRACKING
        self.enable_counting = ENABLE_COUNTING
        if self.enable_tracking:
            from core.inference.sort import Sort   # Sort Class object
            self.tracker = Sort(max_age=10, min_hits=1, iou_threshold=0.3)
        self.count = 0
        self.frame_id = 0
        #self.stop_event = threading.Event()
        # For counting logic
        self.crossed_ids = set()
        self.in_count = 0
        self.out_count = 0
        # track previous positions
        self.track_history = {}
        # avoid duplicate counting
        self.counted_ids = set()
        self.line_y = LINE_Y  # horizontal counting line (adjust)
        self.inf_running = False

    def start(self):
        self.inf_running = True
        self.t = threading.Thread(target=self.run_thread, daemon=True)
        self.t.start()
        return

    def stop(self):
        print("Stopping worker...")
        #self.stop_event.set()
        if self.inf_running:
            self.inf_running = False
        self.t.join()

    def run_thread(self):
        #while not self.stop_event.is_set():
        while self.inf_running:
            frame = self.frame_bus.latest()
            if frame is None:
                continue
            detections, det_array = self.detect(frame)  # det_array contains box cordinates and confidence
            tracks = self.track(det_array)              # Get Tracked objects(in boxes) with ids
            tracked_objects = self.build_tracked_objects(detections, tracks)    # Get tracked objects
            self.update_count(tracked_objects)          # Update count of crossed objects

            result = self.build_result(detections, tracked_objects) # Combine all data, tracked objects, count etc
            self.publish(result)                        # Push data to shared memory

            self.frame_id += 1

    def detect(self, frame):
        results = self.model(frame)[0]          # Apply YOLO model
        detections = []
        det_array = []
        for box in results.boxes:               # Each box represents a detected artifact
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = self.model.names[cls]
            if label != "cell phone" and self.enable_tracking:  # This limits the detection to only single artifact
                continue
            detections.append(
                Detection(label, conf, (int(x1), int(y1), int(x2), int(y2)))
            )
            det_array.append([x1, y1, x2, y2, conf])
        if len(det_array) == 0:                 # If nothing was detected, send back zero array
            det_array = np.empty((0, 5))
        else:
            det_array = np.array(det_array)

        return detections, det_array

    def track(self, det_array):
        if not self.enable_tracking:
            return []
        # return tracked object(in box) with Ids list
        return self.tracker.update(det_array)

    def build_tracked_objects(self, detections, tracks):
        tracked_objects = []
        if self.enable_tracking:
            for t in tracks:
                x1, y1, x2, y2, track_id = t.astype(int)
                # Extract a list of tracked objects
                tracked_objects.append(
                    TrackedObject(
                        track_id=track_id,
                        label="person",
                        confidence=1.0,
                        bbox=(x1, y1, x2, y2)
                    )
                )
        else:
           # No tracked Objects. Use detected objects with Track ID -1
            for det in detections:
                tracked_objects.append(
                    TrackedObject(
                        track_id=-1,
                        label=det.label,
                        confidence=det.confidence,
                        bbox=det.bbox
                    )
                )
        return tracked_objects

    def update_count(self, tracked_objects):
        if not self.enable_counting:
            return
        for obj in tracked_objects:
            if obj.track_id == -1:
                continue
            x1, y1, x2, y2 = obj.bbox
            # Find centre point of object
            cy = (y1 + y2) // 2
            track_id = obj.track_id
            # first appearance
            if track_id not in self.track_history:
                self.track_history[track_id] = cy
                continue
            prev_cy = self.track_history[track_id]
            # DOWN crossing (IN)
            if prev_cy < self.line_y and cy >= self.line_y:
                if (track_id, "IN") not in self.counted_ids:
                    self.in_count += 1
                    self.counted_ids.add((track_id, "IN"))
                    print(f"IN count: {self.in_count}")
            # UP crossing (OUT)
            elif prev_cy > self.line_y and cy <= self.line_y:
                if (track_id, "OUT") not in self.counted_ids:
                    self.out_count += 1
                    self.counted_ids.add((track_id, "OUT"))
                    print(f"OUT count: {self.out_count}")
            # update history
            self.track_history[track_id] = cy

    def build_result(self, detections, tracked_objects):
        return Result(
            frame_id=self.frame_id,
            detections=detections,
            tracks=tracked_objects,
            in_count=self.in_count if self.enable_counting else 0,
            out_count=self.out_count if self.enable_counting else 0
        )

    def publish(self, result):
        self.result_bus.publish(result)

    #def run(self):
    #    while self.running:
    #        frame = self.frame_bus.get()
    #        result = self.process(frame)
    #        self.result_bus.publish(result)

