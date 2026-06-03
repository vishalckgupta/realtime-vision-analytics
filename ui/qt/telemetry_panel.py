from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer

from core.telemetry.metrics import metrics


class TelemetryPanel(QWidget):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Telemetry")

        self.layout = QVBoxLayout()

        self.capture_fps_label = QLabel()
        self.inference_fps_label = QLabel()
        self.stream_fps_label = QLabel()

        self.inference_latency_label = QLabel()
        self.end_to_end_label = QLabel()

        self.dropped_label = QLabel()

        self.layout.addWidget(self.capture_fps_label)
        self.layout.addWidget(self.inference_fps_label)
        self.layout.addWidget(self.stream_fps_label)

        self.layout.addWidget(self.inference_latency_label)
        self.layout.addWidget(self.end_to_end_label)

        self.layout.addWidget(self.dropped_label)

        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(500)

    def update_metrics(self):

        snap = metrics.snapshot()

        self.capture_fps_label.setText(
            f"Capture FPS: {snap['capture_fps']}"
        )

        self.inference_fps_label.setText(
            f"Inference FPS: {snap['inference_fps']}"
        )

        self.stream_fps_label.setText(
            f"Stream FPS: {snap['stream_fps']}"
        )

        self.inference_latency_label.setText(
            f"Inference Latency: {snap['inference_latency_ms']} ms"
        )

        self.end_to_end_label.setText(
            f"End-to-End Latency: {snap['end_to_end_latency_ms']} ms"
        )

        self.dropped_label.setText(
            f"Dropped Frames: {snap['dropped_frames']}"
        )


