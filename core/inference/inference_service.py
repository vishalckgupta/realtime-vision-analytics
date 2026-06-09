# core/inference/inference_service.py

from core.config.settings import *
from core.app.service import BaseService
import time
import threading
from core.contracts.schemas import Detection, Result, TrackedObject
import numpy as np
from core.telemetry.metrics import metrics
from core.inference.detector_factory import DetectorFactory

class InferenceService(BaseService):
    def __init__(self, fbus, rbus, w=FRAME_Y, h=FRAME_X):
        super().__init__("InferenceService")
        self.frame_bus = fbus
        self.result_bus = rbus
        self.enable_tracking = ENABLE_TRACKING
        self.enable_counting = ENABLE_COUNTING
        self.detector = DetectorFactory.create(enable_tracking=self.enable_tracking)
        if self.enable_tracking:
            from core.inference.sort import Sort   # Sort Class object
            self.tracker = Sort(max_age=10, min_hits=1, iou_threshold=0.3)
        self.count = 0
        self.frame_id = 0
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
        while self.inf_running:
            metrics.inference_fps.tick()
            packet = self.frame_bus.latest()
            if packet is None:
                print("InferenceLoop=> No packet")
                continue
            frame = packet.frame
            capture_ts = packet.capture_ts
            if frame is None:
                print("InferenceLoop=> No frame in packet")
                continue
            packet.inference_start_ts = time.monotonic()
            detections, det_array = self.detect(frame)  # det_array contains box cordinates and confidence
            tracks = self.track(det_array)              # Get Tracked objects(in boxes) with ids
            tracked_objects = self.build_tracked_objects(detections, tracks)    # Get tracked objects
            self.update_count(tracked_objects)          # Update count of crossed objects

            result = self.build_result(detections, tracked_objects) # Combine all data, tracked objects, count etc
            self.publish(result)                        # Push data to shared memory
            now = time.monotonic()
            packet.inference_end_ts = time.monotonic()
            metrics.end_to_end_latency_ms = ( (packet.inference_end_ts - packet.capture_ts) * 1000 )
            self.frame_id += 1

    def detect(self, frame):
        start = time.monotonic()
        detections, det_array = self.detector.detect(frame)
        end = time.monotonic()
        metrics.inference_latency_ms = (end - start) * 1000
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


