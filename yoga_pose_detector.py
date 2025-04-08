import cv2
from ultralytics import YOLO
from PyQt5.QtCore import QThread, pyqtSignal

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
    def run(self):
            self.model = YOLO(r'YOLO\runs\detect\train_03\weights\best.pt')
            self.is_running = True
            self.frame = None
            try:
                while self.is_running:
                    if self.frame is None:
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
        
        