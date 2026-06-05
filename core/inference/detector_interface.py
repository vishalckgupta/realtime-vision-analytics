# core/inference/detector_interface.py

from abc import ABC, abstractmethod

class DetectorInterface(ABC):

    @abstractmethod
    def detect(self, frame):
        pass

