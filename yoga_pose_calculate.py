import cv2
import mediapipe as mp
from PyQt5.QtGui import QFont

from pose_calculate.downward_facing_dog_pose_accuracy import evaluate_downward_facing_dog_pose
from pose_calculate.plank_accuracy import evaluate_plank_pose
from pose_calculate.staff_accuracy import evaluate_staff_pose
from pose_calculate.trigle_angle import analyze_image         
from pose_calculate.warrior1_accuracy import evaluate_warrior1_pose
from pose_calculate.warrior2_accuracy import evaluate_warrior2_pose
from pose_calculate.warrior3_accuracy import evaluate_warrior3_pose
from pose_calculate.bridge_angle import evaluate_bridge_pose   
from pose_calculate.locust_accuracy import evaluate_locust_pose
from pose_calculate.squat_accuracy import evaluate_squat_pose  


mp_pose = mp.solutions.pose
POSE = mp_pose.Pose(static_image_mode=False)


INDEX_TO_KEY = {
    0: "downward_facing_dog",
    1: "warrior1",
    2: "warrior2",
    3: "warrior3",
    4: "plank",
    5: "staff",
    6: "squat",      
    7: "locust",
    8: "triangle",
    9: "bridge",
}

KEY_TO_DISPLAY = {
    "downward_facing_dog": "Downward Facing Dog",
    "warrior1": "Warrior I",
    "warrior2": "Warrior II",
    "warrior3": "Warrior III",
    "plank": "Plank Pose",
    "staff": "Staff Pose",
    "squat": "Squat Pose",     
    "locust": "Locust Pose",
    "triangle": "Triangle Pose",
    "bridge": "Bridge Pose",
}


POSE_EVALUATORS = {
    "downward_facing_dog": evaluate_downward_facing_dog_pose,
    "warrior1": evaluate_warrior1_pose,
    "warrior2": evaluate_warrior2_pose,
    "warrior3": evaluate_warrior3_pose,
    "plank": evaluate_plank_pose,
    "staff": evaluate_staff_pose,
    "squat": evaluate_squat_pose,       
    "locust": evaluate_locust_pose,
    "triangle": analyze_image,
    "bridge": evaluate_bridge_pose,     
}

def evaluate_and_display_pose(frame, pose_index, label_widget):
    pose_key = INDEX_TO_KEY.get(pose_index)
    if pose_key is None:
        font = QFont("Arial", 18)
        label_widget.setFont(font)
        label_widget.setPlainText("Unknown pose")
        return

    display_name = KEY_TO_DISPLAY.get(pose_key, pose_key.title())

    
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = POSE.process(image_rgb)

    if not result.pose_landmarks:
        font = QFont("Arial", 16)
        label_widget.setFont(font)
        label_widget.setPlainText(f"{display_name} — No pose detected")
        return

    
    evaluator = POSE_EVALUATORS.get(pose_key)
    if callable(evaluator):
        scores = evaluator(result.pose_landmarks.landmark)  
    else:
        scores = 0.0  

    avg = float(scores) if scores is not None else 0.0

    # 顯示文字
    text = f"{display_name} {avg:.1f}"
    if len(text) > 20:
        font_size = 14
    elif len(text) > 15:
        font_size = 16
    elif len(text) > 10:
        font_size = 18
    else:
        font_size = 20

    font = QFont("Arial", font_size)
    label_widget.setFont(font)
    label_widget.setPlainText(text)


