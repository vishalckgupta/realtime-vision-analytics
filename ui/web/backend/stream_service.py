# ui/web/backend/stream_service.py

import cv2
import gi
import time
import threading
import numpy as np
gi.require_version("Gst", "1.0")
from gi.repository import Gst
from core.app.service import BaseService
from core.telemetry.metrics import metrics

class StreamService(BaseService):
    def __init__(self, frame_bus, result_bus, width, height):
        super().__init__("StreamService")
        self.frame_bus = frame_bus
        self.result_bus = result_bus
        print("StreamService Initializing")
        self.width = width
        self.height = height
        Gst.init(None)
        self.pipeline = None
        self.appsrc = None
        self.running = False

    def build_pipeline(self):
        pipeline_str = f"""
        appsrc name=mysrc is-live=true block=true format=time caps=video/x-raw,format=BGR,width={self.width},height={self.height},framerate=15/1 ! queue !
        videoconvert ! video/x-raw,format=I420 ! avenc_mpeg1video bitrate=1500 !
        mpegtsmux ! tcpserversink host=0.0.0.0 port=9002 sync=false
        """
        self.pipeline = Gst.parse_launch(pipeline_str)
        self.appsrc = self.pipeline.get_by_name("mysrc")
        self.appsrc.set_property("emit-signals", False)
        self.appsrc.set_property("stream-type", 0)
        self.appsrc.set_property("format", Gst.Format.TIME)
        self.appsrc.set_property("is-live", True)
        self.appsrc.set_property("block", True)
        caps = Gst.Caps.from_string(f"video/x-raw,format=BGR,width={self.width},height={self.height},framerate=15/1")
        self.appsrc.set_property("caps", caps)
        print("StreamService pipeline built")

    def start(self):
        self.running = True
        print("StreamService Start")
        self.build_pipeline()
        self.pipeline.set_state(Gst.State.PLAYING)
        time.sleep(1)
        self.t = threading.Thread(target=self.run_thread, daemon=True)
        self.t.start()
        super().start()

    def stop(self):
        self.running = False
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
        self.t.join()
        super().stop()

    def run_thread(self):
        print("StreamService Run")
        duration = Gst.util_uint64_scale_int(1, Gst.SECOND, 15)
        self.timestamp = 0
        while self.running:
            print("Stream_service => Trying to pull frame from bus")
            packet = self.frame_bus.latest()
            if packet is None:
                print("Stream_service => No packet recieved")
                time.sleep(0.5)
                continue
            frame = packet.frame.copy()
            if frame is None:
                print("Stream_service => No frame in packet")
                time.sleep(0.01)
                continue
            print(frame.shape, frame.dtype)
            self.draw_results(frame)
            frame = np.ascontiguousarray(frame)
            data = frame.tobytes()
            buffer = Gst.Buffer.new_allocate(None, len(data), None)
            buffer.fill(0, data)
            buffer.pts = self.timestamp
            buffer.dts = self.timestamp
            buffer.duration = duration

            self.timestamp += duration
            retval = self.appsrc.emit("push-buffer", buffer)

            if retval != Gst.FlowReturn.OK:
                print("GST push-buffer failed")
            metrics.stream_fps.tick()
            print(retval)

    def draw_results(self, frame):
        result = self.result_bus.latest()
        if result is None:
            return
        for det in result.detections:
            x1, y1, x2, y2 = det.bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{det.label}:{det.confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #cv2.putText(frame, f"Count: {result.counter}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"IN : {result.in_count}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        cv2.putText(frame, f"OUT: {result.out_count}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

