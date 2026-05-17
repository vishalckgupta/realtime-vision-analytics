import sys
import cv2
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

class QtApp(QWidget):
    def __init__(self, fbus, rbus):
        super().__init__()
        self.fbus = fbus
        self.rbus = rbus
        #self.cleanup_callback = cleanup_callback

        #self.setWindowTitle("Vision System")
        self.label = QLabel()
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Timer for updating frames (~30 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        frame = self.fbus.latest()
        result = self.rbus.latest()

        if frame is None:
            return

        if result:

            cv2.putText(frame,
                    f"IN : {result.in_count}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,255,0),
                    2)

            cv2.putText(frame,
                    f"OUT: {result.out_count}",
                    (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,0,255),
                    2)
            for det in result.detections:
                x1, y1, x2, y2 = det.bbox

                # draw rectangle
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

                # label
                text = f"{det.label} {det.confidence:.2f}"
                cv2.putText(frame, text, (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
            for trk in result.tracks:
                x1, y1, x2, y2 = trk.bbox

                if trk.track_id != -1:
                    text = f"ID {trk.track_id}"
                else:
                    text = trk.label

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                #cv2.putText(frame, text, (x1, y1-10),
                cv2.putText(frame, text, (20, 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        # Convert BGR → RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        line_y = h // 2
        cv2.line(frame, (0, line_y), (w, line_y), (255, 0, 0), 2)

        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qt_image))

#    def keyPressEvent(self, event):
#        if event.key() == Qt.Key_Q:
#            print("Q pressed → exiting")
#            self.close()

#    def closeEvent(self, event):
#        print("Window closing...")
#        self.cleanup_callback()
#        event.accept()

#def run_qt(fbus, rbus):
#    app = QApplication(sys.argv)
#    window = QtApp(fbus, rbus)
#    window.show()
#    sys.exit(app.exec_())

