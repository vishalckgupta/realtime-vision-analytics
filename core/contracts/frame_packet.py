# core/contracts/frame_packet.py

from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class FramePacket:

    frame_id: int

    capture_ts: float

    frame: np.ndarray

    inference_start_ts: Optional[float] = None
    inference_end_ts: Optional[float] = None

    metadata: Optional[dict] = None

