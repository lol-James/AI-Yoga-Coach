import cv2
from ultralytics import YOLO
from PyQt5.QtCore import QThread, pyqtSignal
import logging
import mediapipe as mp

# Suppress verbose YOLO logging to keep console output clean
logging.getLogger('ultralytics').setLevel(logging.WARNING)


class YogaPoseDetector(QThread):
    """
    A PyQt thread that uses YOLO for pose classification
    and MediaPipe for body visibility checking.
    It emits real-time results to the GUI via signals.
    """

    # Signal emitted with the processed (annotated) image frame
    result_image_signal = pyqtSignal(object)
    # Signal emitted with the detected pose index (integer)
    result_pose_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.frame = None                     # Stores the current frame from the camera
        self.model = None                     # Will hold the YOLO model once loaded

        # List of supported yoga pose names corresponding to YOLO class indices
        self.pose_names = [
            'Downward-Facing_Dog',
            'Warrior_I',
            'Warrior_II',
            'Warrior_III',
            'Plank_Pose',
            'Staff_Pose',
            'Chair_Pose',
            'Locust_Pose',
            'Triangle_Pose',
            'Bridge_Pose'
        ]

        self.is_running = False               # Flag controlling the thread loop (run/stop)

        # Initialize MediaPipe Pose estimator to check full-body visibility
        self.pose_estimator = mp.solutions.pose.Pose(
            static_image_mode=False,          # Process video stream continuously
            model_complexity=1,               # Medium complexity for faster inference
            enable_segmentation=False,        # Segmentation not required here
            min_detection_confidence=0.5,     # Minimum confidence for detection
            min_tracking_confidence=0.45      # Minimum confidence for landmark tracking
        )

        # YOLO detection status flags
        self.yolo_has_person = False          # Whether YOLO detected a person in the frame
        self.yolo_label_name = ""             # Label name of the detected pose (string)

    def is_full_body_visible(self, frame):
        """
        Use MediaPipe to verify if the full body is visible in the current frame.
        Returns True if more than 26 keypoints have good visibility (>0.5).
        """
        # Convert BGR (OpenCV format) to RGB for MediaPipe processing
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Perform pose estimation
        results = self.pose_estimator.process(image_rgb)
        # If landmarks are detected
        if results.pose_landmarks:
            # Extract visibility values for all keypoints
            visible_points = [lm.visibility for lm in results.pose_landmarks.landmark]
            # Check if at least 27 landmarks have high visibility
            if sum(v > 0.5 for v in visible_points) > 26:
                return True
        return False

    def run(self):
        """
        Main thread loop.
        Loads YOLO model and continuously performs detection on the latest frame.
        Emits results (pose and annotated frame) back to the GUI.
        """
        # Load the trained YOLO model (update path as needed)
        self.model = YOLO(r'YOLO\runs\detect\train\weights\best.pt')
        self.is_running = True
        self.frame = None

        try:
            # Main loop runs while the thread is active
            while self.is_running:
                # Skip iteration if there is no frame available
                if self.frame is None:
                    continue

                # Skip detection if the full body is not visible
                if not self.is_full_body_visible(self.frame):
                    # Emit the current (unmodified) frame to the UI
                    self.result_image_signal.emit(self.frame)
                    continue

                # Run YOLO detection on the current frame
                results = self.model(self.frame)

                # Filter out low-confidence detections (confidence threshold = 0.65)
                filtered_results = [res for res in results[0].boxes.data if res[-2] > 0.65]
                results[0].boxes.data = filtered_results

                # If YOLO found valid detections
                if filtered_results:
                    self.yolo_has_person = True

                    # Choose the detection with the highest confidence score
                    best_result = max(filtered_results, key=lambda x: x[-2])
                    pose_index = int(best_result[-1])  # Get class index (pose type)

                    # If pose index is valid, set its name
                    if 0 <= pose_index < len(self.pose_names):
                        self.yolo_label_name = self.pose_names[pose_index]
                    else:
                        self.yolo_label_name = ""

                    # Emit the detected pose index to the GUI
                    self.result_pose_signal.emit(pose_index)

                else:
                    # If no detections found, mark person as not detected
                    self.yolo_has_person = False
                    self.yolo_label_name = ""
                    # Emit a default or fallback pose index (8 = Triangle_Pose here)
                    self.result_pose_signal.emit(8)

                # Generate annotated frame with bounding boxes and labels
                annotated_frame = results[0].plot()
                # Emit the annotated frame for display in GUI
                self.result_image_signal.emit(annotated_frame)

        except Exception as e:
            # Catch and log any runtime errors in the detection loop
            print(f"Error: {e}")

    def stop(self):
        """
        Safely stop the detection thread.
        Sets the running flag to False and waits for thread completion.
        """
        self.is_running = False
        self.wait()
