from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import numpy as np

class CameraThread(QThread):
    new_frame = pyqtSignal(object) 

    def __init__(self):
        super().__init__()
        self.is_running = False
        self.cap = cv2.VideoCapture(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)

        self.music_note_img = cv2.imread('icons/music_note.png', cv2.IMREAD_UNCHANGED)  

    def run(self):
        self.is_running = True
        while self.is_running:
            ret, frame = self.cap.read()
            frame = cv2.flip(frame, 1)
            if ret:
                self.add_music_note_symbol(frame) 
                self.new_frame.emit(frame)  

    def add_music_note_symbol(self, frame):
        """Add the music note symbol to the top-left corner of the frame."""
        if self.music_note_img is not None:
            resized_note = cv2.resize(self.music_note_img, (50, 50))
            resized_height, resized_width = resized_note.shape[:2]
            bgr_note = resized_note[:, :, :3]  
            alpha_note = resized_note[:, :, 3]  
            roi = frame[0:resized_height, 0:resized_width]
            _, mask = cv2.threshold(alpha_note, 1, 255, cv2.THRESH_BINARY)
            frame[0:resized_height, 0:resized_width] = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(mask))
            frame[0:resized_height, 0:resized_width] += cv2.bitwise_and(bgr_note, bgr_note, mask=mask)

    def stop(self):
        self.is_running = False
        self.wait()
