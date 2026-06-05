# core/ingestion/frame_callback.py

import numpy as np
from gi.repository import Gst
from core.telemetry.metrics import metrics
import time
from core.contracts.frame_packet import FramePacket
from core.config.settings import *

class FrameCallback:
    def __init__(self, bus):
        self.bus = bus
        self.frame_id = 0

    def on_new_sample(self, sink):
        metrics.capture_fps.tick()
        sample = sink.emit("pull-sample")
        buffer = sample.get_buffer()
        #caps = sample.get_caps()

        #structure = caps.get_structure(0)
        width = FRAME_X
        height = FRAME_Y

        success, map_info = buffer.map(Gst.MapFlags.READ)
        if not success:
            return Gst.FlowReturn.ERROR

        frame = np.frombuffer(map_info.data, dtype=np.uint8)
        frame = frame.reshape((height, width, 3))

        # For DEBUG
        #print("FrameCallback => Packet Pushed")
        packet = FramePacket(
            frame_id=self.frame_id,
            capture_ts=time.monotonic(),
            frame=frame
        )
        self.frame_id += 1
        self.bus.publish(packet)

        buffer.unmap(map_info)
        return Gst.FlowReturn.OK

