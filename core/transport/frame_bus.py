# core/transport/frame_bus.py

from core.transport.shm_bus import SharedMemoryBus

class FrameBus:
    def __init__(self, bus):
        self.bus = bus

    def publish(self, frame):
        self.bus.write_frame(frame)

    def latest(self):
        return self.bus.read_frame()

    def cleanup(self):
        print("FrameBus Cleanup")
        try:
            self.shm.cleanup()
        except:
            pass

