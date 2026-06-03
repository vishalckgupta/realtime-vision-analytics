import time
import threading
from collections import deque


class RollingFPS:
    def __init__(self, window_size=30):
        self.timestamps = deque(maxlen=window_size)

    def tick(self):
        self.timestamps.append(time.monotonic())

    def get_fps(self):
        if len(self.timestamps) < 2:
            return 0.0

        elapsed = self.timestamps[-1] - self.timestamps[0]

        if elapsed <= 0:
            return 0.0

        return (len(self.timestamps) - 1) / elapsed


class MetricsStore:

    def __init__(self):

        self.lock = threading.Lock()

        self.capture_fps = RollingFPS()
        self.inference_fps = RollingFPS()
        self.stream_fps = RollingFPS()

        self.capture_latency_ms = 0.0
        self.inference_latency_ms = 0.0
        self.encode_latency_ms = 0.0
        self.end_to_end_latency_ms = 0.0

        self.dropped_frames = 0

    def snapshot(self):

        with self.lock:

            return {
                "capture_fps": round(self.capture_fps.get_fps(), 1),
                "inference_fps": round(self.inference_fps.get_fps(), 1),
                "stream_fps": round(self.stream_fps.get_fps(), 1),

                "capture_latency_ms": round(self.capture_latency_ms, 1),
                "inference_latency_ms": round(self.inference_latency_ms, 1),
                "encode_latency_ms": round(self.encode_latency_ms, 1),
                "end_to_end_latency_ms": round(self.end_to_end_latency_ms, 1),

                "dropped_frames": self.dropped_frames
            }


metrics = MetricsStore()

