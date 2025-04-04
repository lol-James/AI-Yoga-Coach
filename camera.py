from PyQt5.QtCore import QThread, pyqtSignal
import cv2

class CameraThread(QThread):
    new_frame = pyqtSignal(object)  # signal used to transmit images
    def __init__(self):
        super().__init__()
        self.is_running = False
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
        
    def run(self):
        self.is_running = True
        while self.is_running:
            ret, frame = self.cap.read()
            frame = cv2.flip(frame, 1)
            if ret:
                self.new_frame.emit(frame)  # Emit frame (to gui)
        # self.cap.release()  # Release camera resources

    def stop(self):
        self.is_running = False
        self.wait() 
