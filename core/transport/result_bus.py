# core/transport/result_bus.py

from core.transport.shm_bus import SharedMemoryBus

class ResultBus:
    def __init__(self, bus):
        self.bus = bus

    def publish(self, result):
        self.bus.publish_result(result)

    def latest(self):
        return self.bus.get_result()

    def cleanup(self):
        print("ResultBus Cleanup")
        try:
            self.shm.cleanup()
        except:
            pass
