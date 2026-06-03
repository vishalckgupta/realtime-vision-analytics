# apps/run_api.py

from core.config.settings import *
from core.transport.shm_bus import SharedMemoryBus
from core.transport.frame_bus import FrameBus
from core.transport.result_bus import ResultBus
from core.app.application import VisionApplication
from core.ingestion.gst_service import GstService
from core.inference.inference_service import InferenceService
from ui.web.backend.server import app
from ui.web.backend.stream_service import StreamService
import uvicorn
import signal

bus = SharedMemoryBus("video_frames", (FRAME_Y, FRAME_X, 3), create=True)
f_bus = FrameBus(bus)
vision = VisionApplication()
gst = GstService(f_bus, FRAME_X, FRAME_Y, INPUT_INTERNAL, STREAM_MPEGTS)
vision.add_service(gst)
vision.add_resource(f_bus)
r_bus = ResultBus(bus)
inf = InferenceService(f_bus, r_bus, FRAME_Y, FRAME_X)
vision.add_service(inf)
vision.add_resource(r_bus)
stream_service = StreamService(f_bus, r_bus, FRAME_X, FRAME_Y)
vision.add_service(stream_service)

# Can be viewed using the following command line gstreamer pipeline
# gst-launch-1.0 tcpclientsrc host=127.0.0.1 port=9001 ! queue leaky=downstream max-size-buffers=2 ! tsdemux ! h264parse ! avdec_h264 ! autovideosink sync=false
# Although the stream is not perfectly non glitchy, it gets stuck and is not giving best results

#configure(f_bus, r_bus, vision.stop_event)

def shutdown(*args):
    print("Shutdown request")
    vision.stop()

signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

try:
    vision.start()
    uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000
            )
except KeyboardInterrupt:
    print("Shutdown request")
finally:
    vision.stop()

