# core/contracts/schemas.py


from dataclasses import dataclass
from typing import List

@dataclass
class Detection:
    label: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)

@dataclass
class TrackedObject:
    track_id: int
    label: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)

@dataclass
class Result:
    frame_id: int
    detections: List[Detection]
    tracks: List[TrackedObject] # NEW
    in_count: int
    out_count: int


