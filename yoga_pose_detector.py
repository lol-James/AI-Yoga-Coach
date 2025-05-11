import cv2
from ultralytics import YOLO
from PyQt5.QtCore import QThread, pyqtSignal
import logging
import mediapipe as mp

logging.getLogger('ultralytics').setLevel(logging.WARNING)

class YogaPoseDetector(QThread):
    result_image_signal = pyqtSignal(object)  # labelled image
    result_pose_signal = pyqtSignal(int)  # detected pose index

    def __init__(self):
        super().__init__()
        self.frame = None
        self.model = None
        self.pose_names = ['Downward-Facing_Dog', 'Warrior_I', 'Warrior_II', 'Cow_Pose', 'Plank_Pose', 'Staff_Pose',
                           'Squat_Pose', 'Locust_Pose', 'Triangle_Pose', 'Bridge_Pose']
        self.is_running = False
        self.pose_estimator = mp.solutions.pose.Pose(static_image_mode=False,
                                                     model_complexity=1,
                                                     enable_segmentation=False,
                                                     min_detection_confidence=0.5,
                                                     min_tracking_confidence=0.45)

    def is_full_body_visible(self, frame):
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose_estimator.process(image_rgb)
        if results.pose_landmarks:
            visible_points = [lm.visibility for lm in results.pose_landmarks.landmark]
            if sum(v > 0.5 for v in visible_points) > 26:
                return True
        return False

    def run(self):
            self.model = YOLO(r'YOLO\runs\detect\train\weights\best.pt')
            self.is_running = True
            self.frame = None
            try:
                while self.is_running:
                    if self.frame is None:
                        continue

                    if not self.is_full_body_visible(self.frame):
                        self.result_image_signal.emit(self.frame) 
                        continue

                    results = self.model(self.frame)
                    filtered_results = [res for res in results[0].boxes.data if res[-2] > 0.65]
                    results[0].boxes.data = filtered_results

                    if filtered_results:
                        best_result = max(filtered_results, key=lambda x: x[-2])
                        pose_index = int(best_result[-1])  
                        self.result_pose_signal.emit(pose_index)
                    else:
                        self.result_pose_signal.emit(8)
                        
                    annotated_frame = results[0].plot()
                    self.result_image_signal.emit(annotated_frame)
            except Exception as e:
                print(f"Error: {e}")
    
    def stop(self):
        self.is_running = False
        self.wait()
        
        