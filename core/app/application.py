# core/app/application.py

import time
import threading

class VisionApplication:

    def __init__(self):
        self.services = []
        self.resources = []
        self.running = False
        self.stop_event = threading.Event()

    def add_service(self, service):
        self.services.append(service)

    def add_resource(self, resource):
        self.resources.append(resource)

    def start(self):
        self.running = True
        for s in self.services:
            s.start()

    def stop(self):
        self.running = False
        self.stop_event.set()
        for s in self.services:
            print("Stopping Service")
            s.stop()
        for s in self.services:
            print("Joining Service")
            s.join()
        print("Resource Cleanup")
        for r in self.resources:
            if hasattr(r, "cleanup"):
                r.cleanup()

    def run(self):
        self.start()
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Shutdown request")
        finally:
            self.stop()

