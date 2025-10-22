import cv2
import mediapipe as mp
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
# Import specific pose evaluation functions from different modules
from pose_calculate.downward_facing_dog_pose_accuracy import evaluate_downward_facing_dog_pose
from pose_calculate.plank_accuracy import evaluate_plank_pose
from pose_calculate.staff_accuracy import evaluate_staff_pose
from pose_calculate.trigle_angle import evaluate_triangle_pose
from pose_calculate.warrior1_accuracy import evaluate_warrior1_pose
from pose_calculate.warrior2_accuracy import evaluate_warrior2_pose
from pose_calculate.warrior3_accuracy import evaluate_warrior3_pose
from pose_calculate.bridge_angle import evaluate_bridge_pose
from pose_calculate.locust_accuracy import evaluate_locust_pose
from pose_calculate.squat_accuracy import evaluate_squat_pose


class PoseCalculate(QObject):
    # Mapping index values to pose names (used to select pose evaluation type)
    INDEX_TO_KEY = {
        0: "downward_facing_dog",
        1: "warrior1",
        2: "warrior2",
        3: "warrior3",
        4: "plank",
        5: "staff",
        6: "chair",
        7: "locust",
        8: "triangle",
        9: "bridge",
    }
    score_result =pyqtSignal(object,object,object) 
    def __init__(self):
        # Initialize MediaPipe pose model
        super().__init__()
        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose(
            static_image_mode=False,          # Use continuous video input, not static images
            model_complexity=2,               # Higher complexity for better accuracy
            enable_segmentation=False,        # Disable segmentation mask
            min_detection_confidence=0.7,     # Minimum confidence for detecting a person
            min_tracking_confidence=0.7       # Minimum confidence for tracking landmarks
        )

        # Human-readable display names for each yoga pose
        self.key_to_display = {
            "downward_facing_dog": "Downward Facing Dog",
            "warrior1": "Warrior I",
            "warrior2": "Warrior II",
            "warrior3": "Warrior III",
            "plank": "Plank Pose",
            "staff": "Staff Pose",
            "chair": "Chair Pose",
            "locust": "Locust Pose",
            "triangle": "Triangle Pose",
            "bridge": "Bridge Pose",
        }

        # Map each pose name to its corresponding evaluation function
        self.pose_evaluators = {
            "downward_facing_dog": evaluate_downward_facing_dog_pose,
            "warrior1": evaluate_warrior1_pose,
            "warrior2": evaluate_warrior2_pose,
            "warrior3": evaluate_warrior3_pose,
            "plank": evaluate_plank_pose,
            "staff": evaluate_staff_pose,
            "chair": evaluate_squat_pose,       # 'Chair' pose uses squat evaluation
            "locust": evaluate_locust_pose,
            "triangle": evaluate_triangle_pose,
            "bridge": evaluate_bridge_pose,
        }

    def evaluate_pose(self, frame, pose_index, label_widget):
        """
        Evaluate a given pose from a video frame.
        Args:
            frame: The input video frame (BGR format from OpenCV)
            pose_index: Integer representing the type of pose to evaluate
            label_widget: PyQt text widget used to display results
        """
        # Get the corresponding pose key (e.g., "warrior1") from the index
        pose_key = PoseCalculate.INDEX_TO_KEY.get(pose_index)
        if pose_key is None:
            # Handle invalid index
            self._set_label(label_widget, "Unknown pose")
            return None

        # Get the human-readable name for display
        display_name = self.key_to_display.get(pose_key, pose_key.title())

        # Convert the OpenCV frame from BGR to RGB for MediaPipe processing
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose_detector.process(image_rgb)

        # Check if pose landmarks were detected
        if not result.pose_landmarks:
            self._set_label(label_widget, f"Error: Pose detected but no landmarks")
            return None

        # Retrieve the correct evaluator function for the current pose
        evaluator = self.pose_evaluators.get(pose_key)
        if callable(evaluator):
            # Pass the landmark data to the evaluator function
            scores = evaluator(result.pose_landmarks.landmark)
        else:
            # If evaluator is missing or invalid, set score to zero
            scores = 0.0

        # Compute the overall (average) score for the pose
        if scores:
            self.score_result.emit(scores,result,frame)
        avg = self._calculate_average_score(scores)

        # Create display text showing pose name and accuracy
        text = f"{display_name} {avg:.1f}"
        # Update the label widget to show the result
        self._set_label(label_widget, text, font_size=12)

        return avg

    def _calculate_average_score(self, scores):
        """
        Compute the average score from a dictionary or numeric input.
        Args:
            scores: Could be a dict of joint scores, or a single number
        Returns:
            A float representing the average score
        """
        if isinstance(scores, dict):
            if "average_score" in scores:
                # Directly use 'average_score' if provided
                return float(scores["average_score"])
            elif len(scores) > 0:
                # Calculate mean of all values in dict
                return float(sum(scores.values()) / len(scores))
            else:
                return 0.0
        elif isinstance(scores, (int, float)):
            # If single numeric score, convert to float
            return float(scores)
        else:
            # Unknown format, return 0
            return 0.0

    def _set_label(self, label_widget, text, font_size=14):
        """
        Helper function to update a PyQt text label with specific font and text.
        Args:
            label_widget: The PyQt text widget to update
            text: The text to display
            font_size: Font size for the label
        """
        font = QFont("Arial", font_size)         # Set font style and size
        label_widget.setFont(font)               # Apply font to widget
        label_widget.setPlainText(text)          # Set label text content
