# apps/run_qt.py

from core.config.settings import *
from core.transport.shm_bus import SharedMemoryBus
from core.transport.frame_bus import FrameBus
from core.transport.result_bus import ResultBus
from core.app.application import VisionApplication
from core.ingestion.gst_service import GstService
from core.inference.inference_service import InferenceService

import signal
import sys
from PyQt5.QtWidgets import QApplication
from ui.qt.qt_app import QtApp

bus = SharedMemoryBus("video_frames", (FRAME_Y, FRAME_X, 3), create=True)
f_bus = FrameBus(bus)
app = VisionApplication()
gst = GstService(f_bus, FRAME_X, FRAME_Y, INPUT_INTERNAL, STREAM_NONE)
app.add_service(gst)
app.add_resource(f_bus)
r_bus = ResultBus(bus)
inf = InferenceService(f_bus, r_bus, FRAME_Y, FRAME_X)
app.add_service(inf)
app.start()

qt_app = QApplication(sys.argv)
window = QtApp(f_bus, r_bus)
window.show()
sys.exit(qt_app.exec())

def shutdown(*args):
    print("Shutdown request")
    app.stop()
    qt_app.quit()

qt_app.aboutToQuit.connect(lambda: vision.stop())
signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)

