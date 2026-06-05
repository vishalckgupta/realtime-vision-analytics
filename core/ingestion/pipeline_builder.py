# core/ingestion/pipeline_builder.py

from core.config.settings import *

# Working pipeline for CCTV Camera for reference
# gst-launch-1.0 rtspsrc location=rtsp://drawingroom:drawingroom@192.168.1.51:554/stream1 ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! autovideosink


def get_source_pipeline(input_mode):
    src_pipe = ""
    if input_mode == INPUT_INTERNAL:
        if DETECTOR_TYPE == "onnx":
            src_pipe = f"libcamerasrc ! video/x-raw,width={FRAME_X},height={FRAME_Y},framerate={FPS}/1  ! videoflip method=rotate-180 ! videoconvert !"
        else:
            src_pipe = f"v4l2src device={CAMERA_DEVICE} ! image/jpeg,width={FRAME_X},height={FRAME_Y} ! jpegdec ! videoconvert !"
    elif input_mode == INPUT_EXTERNAL:
        src_pipe = f"rtspsrc location={RTSP_URL} latency=100 drop-on-latency=true protocols=tcp ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! videoscale ! video/x-raw,width={FRAME_X},height={FRAME_Y} !"
    return src_pipe

def get_mpegts_branch():
    return "queue leaky=downstream max-size-buffers=2 ! videoconvert ! videoscale ! videorate ! video/x-raw,format=I420,width=640,height=480,framerate=15/1 ! avenc_mpeg1video bitrate=1500 ! mpegtsmux ! tcpserversink host=0.0.0.0 port=9001 sync=false"

def get_appsink_branch():
    return f"queue leaky=downstream max-size-buffers=1 ! videoconvert ! video/x-raw,format=BGR ! appsink name=sink emit-signals=true drop=true sync=false max-buffers=1 "

def build_pipeline(input_mode=INPUT_INTERNAL, stream_mode=STREAM_NONE):
    source = get_source_pipeline(input_mode)
    #mid_section = get_mid_section()
    if stream_mode == STREAM_MPEGTS :
        # Split pipline using tee to two branchs one to webRTC, other to appsink
        branch_mpegts = get_mpegts_branch()
        branch_appsink = get_appsink_branch()
        final_pipeline = f"{source} tee name=t t. ! {branch_mpegts} t. ! {branch_appsink}"
    elif stream_mode == STREAM_NONE:
        # Only 1 branch forward to appsink
        branch_appsink = get_appsink_branch()
        final_pipeline = f"{source} {branch_appsink}"
    print(final_pipeline)
    return final_pipeline

def get_webrtc_branch():
    webrtc_pipe = "queue max-size-buffers=2 leaky=downstream ! videoconvert ! webrtcsink name=webrtc  meta=\"meta,name=stream1\" signaling-server-url=\"ws://127.0.0.1:8443\" "
    return webrtc_pipe

