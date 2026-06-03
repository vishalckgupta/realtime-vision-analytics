# core/transport/frame_bus.py

from core.transport.shm_bus import SharedMemoryBus
from core.contracts.frame_packet import FramePacket

class FrameBus:
    def __init__(self, bus):
        self.bus = bus
        self.latest_packet = None

    def publish(self, packet):
        self.latest_packet = packet
        #self.bus.write_frame(packet.frame)

    def latest(self):
        return self.latest_packet
        #return self.bus.read_frame()

    def cleanup(self):
        print("FrameBus Cleanup")
        try:
            self.shm.cleanup()
        except:
            pass

