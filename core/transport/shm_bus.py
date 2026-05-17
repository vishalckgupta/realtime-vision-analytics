# core/mesaging/shm_bus.py

# Uses Multiprocessing schared memory, for exchanging frames and results
# Shall be encapsulated with another layer of APIs

from multiprocessing import shared_memory
import numpy as np
import threading

class SharedMemoryBus:
    def __init__(self, name, shape, create=False):
        self.shape = shape
        self.size = np.prod(shape)
        self.lock = threading.Lock()
        try:
            if create:
                raise FileNotFoundError  # force creation
            self.shm = shared_memory.SharedMemory(name=name)
            print(f"Attached to existing shared memory: {name}")
        except FileNotFoundError:
            print(f"Creating shared memory: {name}")
            self.shm = shared_memory.SharedMemory(
                name=name,
                create=True,
                size=self.size
            )
        self.array = np.ndarray(shape, dtype=np.uint8, buffer=self.shm.buf)
        self.latest_result = None
        self.closed = False

    def write_frame(self, frame):
        if self.closed:
            return
        with self.lock:
            np.copyto(self.array, frame)

    def read_frame(self):
        if self.closed:
            return
        with self.lock:
            return self.array.copy()

    def publish_result(self, result):
        if self.closed:
            return
        with self.lock:
            self.latest_result = result

    def get_result(self):
        if self.closed:
            return
        with self.lock:
            return self.latest_result

    def cleanup(self):
        if self.closed:
            return
        self.closed = True
        print("Cleaning shared memory")
        try:
            self.shm.close()
        except Exception as e:
            print("close error:", e)
        try:
            self.shm.unlink()
        except FileNotFoundError:
            pass
        except Exception as e:
            print("unlink error:", e)

