# Overall project configuration

# Input Stream controls ; mode = Internal / External

#INPUT_MODE = "Internal"
INPUT_INTERNAL = "Internal"
INPUT_EXTERNAL = "External"
CAMERA_DEVICE = "/dev/video0"
RTSP_URL = "rtsp://drawingroom:drawingroom@192.168.1.51:554/stream1"
# GStreamer Controls webRTC / MPEGTS / None

#STREAMING_MODE = "MPEGTS"
STREAM_NONE = "None"
STREAM_MPEGTS = "MPEGTS"

# Camera Resolution
FRAME_X = 640
FRAME_Y = 480
FPS = 15
# Tracking controls
ENABLE_TRACKING = True
ENABLE_COUNTING = True
# Boundary line
LINE_Y = FRAME_Y / 2
# Tracked object
#TRACK_OBJ = "cell phone"
TRACK_OBJ = "person"
