import cv2
import mediapipe as mp
import numpy as np

# 閮�蝞���拙�����憭曇��嚗�摨�
def calculate_angle(a, b):
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return None
    unit_a = a / np.linalg.norm(a)
    unit_b = b / np.linalg.norm(b)
    dot_product = np.dot(unit_a, unit_b)
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
    return np.degrees(angle)

# ���蝺���扯�������賣��
def score_angle(perfect_angle, actual_angle, weight=33.3, tolerance=5, power=2):
    diff = abs(perfect_angle - actual_angle)
    if diff > 90:
        return 0
    elif diff <= tolerance:
        return weight
    else:
        return weight * (1 - ((diff - tolerance) / (90 - tolerance)) ** power)

def evaluate_triangle_pose(landmarks, perfect_trunk=74.74, perfect_pelvis=69.13, perfect_shoulder=170.59):
    def pt(index): 
        return np.array([landmarks[index].x, landmarks[index].y])

    # 1. 身體軸線
    mid_hip = (pt(23) + pt(24)) / 2
    mid_shoulder = (pt(11) + pt(12)) / 2
    trunk_vector = mid_shoulder - mid_hip
    vertical_line = np.array([0, -1])
    angle_trunk = calculate_angle(trunk_vector, vertical_line)

    # 2. 骨盆
    vec_left_leg = pt(23) - pt(25)
    vec_right_leg = pt(24) - pt(26)
    angle_pelvis = calculate_angle(vec_left_leg, vec_right_leg)

    # 3. 肩膀
    vec_left_arm = pt(12) - pt(14)
    vec_right_arm = pt(11) - pt(13)
    angle_shoulder = calculate_angle(vec_left_arm, vec_right_arm)

    if None in [angle_trunk, angle_pelvis, angle_shoulder]:
        return {"average_score": 0.0}

    trunk_score = score_angle(perfect_trunk, angle_trunk)
    pelvis_score = score_angle(perfect_pelvis, angle_pelvis)
    shoulder_score = score_angle(perfect_shoulder, angle_shoulder)

    scores = {
        "Trunk": trunk_score,
        "Pelvis": pelvis_score,
        "Shoulder": shoulder_score,
        "average_score": round((trunk_score + pelvis_score + shoulder_score) , 2)
    }
    return scores