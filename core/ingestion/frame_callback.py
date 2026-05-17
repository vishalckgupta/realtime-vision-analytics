# core/ingestion/frame_callback.py

import numpy as np
from gi.repository import Gst

class FrameCallback:
    def __init__(self, bus):
        self.bus = bus

    def on_new_sample(self, sink):
        sample = sink.emit("pull-sample")
        buffer = sample.get_buffer()
        caps = sample.get_caps()

        structure = caps.get_structure(0)
        width = structure.get_value("width")
        height = structure.get_value("height")

        success, map_info = buffer.map(Gst.MapFlags.READ)
        if not success:
            return Gst.FlowReturn.ERROR

        frame = np.frombuffer(map_info.data, dtype=np.uint8)
        frame = frame.reshape((height, width, 3))

        # For DEBUG
        #print(frame.shape)
        self.bus.publish(frame)

        buffer.unmap(map_info)
        return Gst.FlowReturn.OK

