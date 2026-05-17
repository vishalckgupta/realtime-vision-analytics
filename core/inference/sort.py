import numpy as np

"""
The basic idea of SORT algorithm is asking this simple question
“Which detection in this frame belongs to which object from previous frame?”
YOLO gives detections like
Frame 1
Person at (100,100,200,300)
Frame 2
Person at (110,105,210,305)
SORT says - "That is probably the SAME person." Let me assign same ID
SORT works by - Compare NEW boxes with OLD boxes, using IOU(Intersection over Union)
"""

"""
Function iou() Compares bb_test vs bb_gt
Say there is no overlap, return 0.0 
for a decent match, return 0.5
for almost same object, return 0.9
"""
def iou(bb_test, bb_gt):
    xx1 = np.maximum(bb_test[0], bb_gt[0])
    yy1 = np.maximum(bb_test[1], bb_gt[1])
    xx2 = np.minimum(bb_test[2], bb_gt[2])
    yy2 = np.minimum(bb_test[3], bb_gt[3])

    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)

    inter = w * h
    union = ((bb_test[2]-bb_test[0])*(bb_test[3]-bb_test[1]) +
             (bb_gt[2]-bb_gt[0])*(bb_gt[3]-bb_gt[1]) - inter)

    return inter / union if union > 0 else 0

"""
Each instance of class Track represents One Tracked Object. It stores the following
| Variable | Purpose                |
| -------- | ---------------------- |
| bbox     | latest position        |
| id       | tracking ID            |
| age      | frames since last seen |
| hits     | how many times matched |

"""
class Track:
    def __init__(self, bbox, track_id):
        self.bbox = bbox
        self.id = track_id
        self.age = 0
        self.hits = 1

"""
Class Sort manages ALL active tracks. Its important variables are
| Variable | Purpose                 |
| -------- | ----------------------- |
| tracks   | current tracked objects |
| next_id  | next unique ID          |
"""
class Sort:
    def __init__(self, max_age=10, min_hits=1, iou_threshold=0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.tracks = []
        self.next_id = 1

    def update(self, detections):
        '''
        Function update is the heart of the algorith. 
        As input, it takes 'detections', example:
        [
         [100,100,200,200,0.9],
         [300,300,400,400,0.8]
        ]
        And outputs same boxes + track ids, example
        [
         [100,100,200,200,1],
         [300,300,400,400,2]
        ]

        '''
        updated_tracks = []

        for det in detections:
            matched = False

            for track in self.tracks:
                # For every new detection, compare with existing tracks
                # Meaning  - "Does this new box overlap old track enough?"
                if iou(det[:4], track.bbox) > self.iou_threshold:
                    # If YES, update track position
                    track.bbox = det[:4]
                    track.age = 0
                    track.hits += 1
                    updated_tracks.append(track)
                    matched = True
                    break

            if not matched:
                # If no match found "This must be a NEW object"
                new_track = Track(det[:4], self.next_id)
                self.next_id += 1
                updated_tracks.append(new_track)

        # age tracks
        for track in updated_tracks:
            # "How long since we saw this object?"
            track.age += 1

        # If object disappears, eventually
        # remove old tracks or dead tracks
        self.tracks = [t for t in updated_tracks if t.age < self.max_age]

        # return format: x1,y1,x2,y2,id
        results = []
        for t in self.tracks:
            if t.hits >= self.min_hits:
                x1, y1, x2, y2 = map(int, t.bbox)
                results.append([x1, y1, x2, y2, t.id])

        return np.array(results)

