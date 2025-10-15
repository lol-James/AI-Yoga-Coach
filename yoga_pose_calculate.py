import cv2
import mediapipe as mp
from PyQt5.QtGui import QFont

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


class PoseCalculate:
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
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.7
        )

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

        self.pose_evaluators = {
            "downward_facing_dog": evaluate_downward_facing_dog_pose,
            "warrior1": evaluate_warrior1_pose,
            "warrior2": evaluate_warrior2_pose,
            "warrior3": evaluate_warrior3_pose,
            "plank": evaluate_plank_pose,
            "staff": evaluate_staff_pose,
            "chair": evaluate_squat_pose,
            "locust": evaluate_locust_pose,
            "triangle": evaluate_triangle_pose,
            "bridge": evaluate_bridge_pose,
        }

    def evaluate_pose(self, frame, pose_index, label_widget):
        pose_key = PoseCalculate.INDEX_TO_KEY.get(pose_index)
        if pose_key is None:
            self._set_label(label_widget, "Unknown pose")
            return None

        display_name = self.key_to_display.get(pose_key, pose_key.title())

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose_detector.process(image_rgb)

        if not result.pose_landmarks:
            self._set_label(label_widget, f"Error: Pose detected but no landmarks")
            return None

        evaluator = self.pose_evaluators.get(pose_key)
        if callable(evaluator):
            scores = evaluator(result.pose_landmarks.landmark)
        else:
            scores = 0.0

        avg = self._calculate_average_score(scores)
        text = f"{display_name} {avg:.1f}"
        self._set_label(label_widget, text, font_size=12)

        return avg

    def _calculate_average_score(self, scores):
        if isinstance(scores, dict):
            if "average_score" in scores:
                return float(scores["average_score"])
            elif len(scores) > 0:
                return float(sum(scores.values()) / len(scores))
            else:
                return 0.0
        elif isinstance(scores, (int, float)):
            return float(scores)
        else:
            return 0.0

    def _set_label(self, label_widget, text, font_size=14):
        font = QFont("Arial", font_size)
        label_widget.setFont(font)
        label_widget.setPlainText(text)
