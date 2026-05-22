# core/ingestion/gst_service.py

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
from core.ingestion.frame_callback import FrameCallback
from core.config.settings import *
from core.app.service import BaseService
from core.ingestion.pipeline_builder import *

class GstService(BaseService):
    def __init__(self, bus, w=FRAME_X, h=FRAME_Y, input_mode=INPUT_INTERNAL, stream_mode=STREAM_NONE):
        super().__init__("GstService")
        Gst.init(None)
        self.bus = bus
        self.width = w
        self.height = h

        self.loop = GLib.MainLoop()
        #self.running = True

        #self.pipeline = Gst.parse_launch(
        #    f"v4l2src device=/dev/video0 ! "
        #    f"image/jpeg,framerate=15/1,width={self.width},height={self.height} ! "
        #    f"jpegdec ! videoconvert ! video/x-raw,format=RGB ! "  
        #    f"appsink name=sink emit-signals=true drop=true sync=false max-buffers=1 "
        #)
        self.pipeline = Gst.parse_launch(build_pipeline(input_mode, stream_mode))
        self.sink = self.pipeline.get_by_name("sink")
        if not self.sink:
            raise RuntimeError("appsink not found in pipeline")
        callback = FrameCallback(self.bus)
        self.sink.connect("new-sample", callback.on_new_sample)

    def start(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        #while self.running:
        #    time.sleep(0.1)

    def stop(self):
        print("Stopping GST State")
        self.pipeline.set_state(Gst.State.NULL)
        if self.loop:
            print("Stopping GST loop")
            self.loop.quit()

