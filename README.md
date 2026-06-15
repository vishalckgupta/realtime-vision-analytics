# Realtime Vision Analytics Framework

A modular realtime computer vision framework built using Python, GStreamer, OpenCV, YOLO, Qt and FastAPI.

This project demonstrates a scalable architecture for:
- realtime video ingestion
- AI inference
- object tracking
- line crossing analytics
- shared memory IPC
- Qt desktop visualization
- network video streaming

The framework is designed with an industrial-style modular architecture, emphasizing:
- service-oriented threading
- clean shutdown handling
- decoupled messaging buses
- realtime streaming pipelines
- incremental scalability

---

## Project Demo

Watch the demo video:

https://youtu.be/AS2aLneFbEA


# Features

## Realtime Camera Ingestion
- GStreamer-based video capture
- Low-latency frame acquisition
- Configurable resolution and FPS

## AI Inference
- YOLO-based object detection
- Modular inference worker
- Shared-memory frame processing

## Object Tracking
- SORT-style tracking support
- Persistent object IDs
- Track lifecycle management

## Line Crossing Counter
- Virtual line crossing detection
- Direction-aware counting
- Event-based analytics

## Multiple Output Modes

### Qt Desktop Viewer
- Live annotated video display
- Bounding boxes and tracking overlays
- FPS and analytics visualization

### Web/API Viewer
- FastAPI-based backend
- Browser-accessible stream
- Remote monitoring capability

### MPEGTS Streaming
- GStreamer appsrc-based streaming
- MPEGTS transport over TCP
- Remote GStreamer client support

## IPC and Messaging
- Shared memory frame transport
- Thread-safe frame bus
- Decoupled result bus architecture

## Clean Threading Architecture
- BaseService abstraction
- Unified thread lifecycle management
- Graceful shutdown handling

---

# High-Level Architecture

```text

+-----------------------------------------------------------------------------------+
|                           Realtime Vision Analytics                               |
+-----------------------------------------------------------------------------------+

+-------------------+
| Camera / RTSP     |
+-------------------+
          |
          v
+-------------------+
| GStreamer Input   |
+-------------------+
          |
          v
+-------------------+
| Frame Callback    |
+-------------------+
          |
          v
+-------------------+
| Shared Memory Bus |
+-------------------+
          |
          v
+-------------------+
| Inference Thread  |
+-------------------+
          |
          v
+-------------------+
| Tracker / Counter |
+-------------------+
          |
          v
+-------------------+
| Qt Visualization  |
+-------------------+

```

## Detector Layer

```text

          Detector Factory
                 |
       +---------+---------+
       |                   |
       v                   v
 Ultralytics         ONNX Runtime
  (Ubuntu)          (Raspberry Pi)

```

Note: Web/API Streamer is still work in progress, I still have not got a glitch free output yet

# Technologies Used

- Python 3
- GStreamer
- OpenCV
- Ultralytics YOLO
- NumPy
- PyQt5
- FastAPI
- Uvicorn
- Shared Memory IPC
- Multithreading

# Project structure

```
vision_system/
│
├── apps/
│   ├── run_qt.py
│   ├── run_api.py
│   └── run_headless.py
│
├── core/
│   ├── app/
│   ├── config/
│   ├── ingestion/
│   ├── inference/
│   ├── contracts/
│   ├── transport/
│   ├── visualization/
│   ├── TBD/
│   └── models/
│
├── ui/
│   ├── qt/
│   └── web/
│       └── frontend/
│       └── backend/
│
└── README.md
```

# Installation

## Create Virtual Environment

```
python3 -m venv venv
source venv/bin/activate
```

## Install Python Dependencies

`pip install ultralytics opencv-python numpy fastapi uvicorn PyQt5`

## Install GStreamer Dependencies (Ubuntu)

```
sudo apt install \
gstreamer1.0-tools \
gstreamer1.0-plugins-base \
gstreamer1.0-plugins-good \
gstreamer1.0-plugins-bad \
gstreamer1.0-plugins-ugly \
python3-gi \
gir1.2-gstreamer-1.0
```


# Running the Project

## QT Desktop Mode

`python -m apps.run_qt`

## Web/API Mode

`python -m apps.run_api`

Then open in browser

`http://localhost:8000`

## Headless Mode

`python -m apps.run_headless`

# Remote MPEGTS Stream Viewing

## Run Stream Server

Start API mode or streaming mode.

## Connect From Remote Client

```
gst-launch-1.0 \
tcpclientsrc host=<SERVER_IP> port=9001 \
! tsdemux \
! decodebin \
! autovideosink
```

# Current Capabilities

- Realtime object detection
- Shared memory frame exchange
- Qt visualization
- FastAPI integration
- MPEGTS streaming
- Thread-safe architecture
- Line crossing analytics
- Modular services
- Graceful shutdown support

# Planned Improvements

## Performance

* GPU acceleration
* TensorRT optimization
* Hardware encoding
* Zero-copy pipelines

## Streaming

* RTSP support
* RTP multicast
* WebRTC support

## Analytics

* Multi-zone counting
* Direction analytics
* Heatmaps
* Event logging

## Architecture Highlights

- Modular GStreamer-based ingestion pipeline
- Supports both USB cameras and RTSP IP cameras
- Low-latency tee-based dual-stream architecture
- Parallel AI inference and raw-stream monitoring
- OpenCV + YOLO object detection/tracking
- Browser-based live monitoring using WebSockets + JSMpeg
- Multi-process scalable design
- Shared-memory frame transport for AI pipeline
- Designed for Linux and Raspberry Pi deployment

# Engineering Goals

This project is intended as a learning and engineering platform for:

* realtime systems
* multimedia pipelines
* AI video analytics
* distributed video systems
* low-latency streaming
* modular software architecture


# Notes

This project is under active development and evolving incrementally toward a more industrial-grade realtime analytics framework.

The current implementation prioritizes:

* architectural clarity
* modularity
* debugging visibility
* realtime experimentation

over raw production optimization.

# Author

Vishal Ck Gupta

22+ years of hands-on engineering experience in:

* Linux systems
* C/C++
* Python
* video pipelines
* multimedia systems
* robotics
* realtime architectures


