# core/app/service.py
# This is the Base Service class that gives start(), stop(), run() controls
# uniformly to any class that inherits this class

import threading


class BaseService:

    def __init__(self, name):
        # Class gets registered here
        self.name = name
        # Initial state is NOT RUNNING
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.tread = threading.Thread(
            target=self.run)
        #    daemon=True )
        self.thread.start()

    def stop(self):
        self.running = False

    def join(self):
        print("Inside Service Class, Joining")
        if self.thread:
            print(f"Joining {self.name}")
            self.thread.join()
            print(f"{self.name} Joined")

    def run(self):
        raise NotImplementedError

