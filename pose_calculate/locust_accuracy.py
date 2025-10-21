import os
import cv2
import numpy as np
import mediapipe as mp

def calculate_angle(a, b, c):
    a, b, c = np.array(a, dtype=float), np.array(b, dtype=float), np.array(c, dtype=float)
    ba = a - b
    bc = c - b
    denom = np.linalg.norm(ba) * np.linalg.norm(bc)
    if denom < 1e-6:
        return 0.0
    cosine_angle = np.dot(ba, bc) / denom
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return float(np.degrees(angle))

TOLERANCE = 5
POWER = 2

def score_with_tolerance(actual_angle, angle_info):
    diff = abs(actual_angle - angle_info["avg"])
    if diff < 5:
        return 100.0
    elif 5 <= diff <= 50:
        return round(100 * (1 - ((diff - TOLERANCE) / (50 - TOLERANCE)) ** POWER), 2)
    else:
        return 0.0

STANDARD_ANGLES_LOCUST = {
    "back_body": {"avg": 135.90},  # ?-?-?
    "leg_straight":     {"avg": 159.37},  # ?-?-?
    "armpit":     {"avg": 31.42},   # ?-?-?
    "upper_body":    {"avg": 163.04},  # ?-?-?
}

def evaluate_locust_pose(landmarks):
    def P(landmarks, i):
        return [landmarks[i].x, landmarks[i].y]

    LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
    LEFT_ELBOW, RIGHT_ELBOW = 13, 14
    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_KNEE, RIGHT_KNEE = 25, 26
    LEFT_ANKLE, RIGHT_ANKLE = 27, 28
    NOSE = 0

    scores = {}

    # BackLow??-?-?????
    LEFT_back_angle = calculate_angle(P(landmarks, LEFT_SHOULDER), P(landmarks, LEFT_HIP), P(landmarks, LEFT_KNEE))
    Right_back_angle = calculate_angle(P(landmarks, RIGHT_SHOULDER), P(landmarks, RIGHT_HIP), P(landmarks, RIGHT_KNEE))
    LEFT_back_score = (score_with_tolerance(LEFT_back_angle, STANDARD_ANGLES_LOCUST["back_body"]))
    Right_back_score = (score_with_tolerance(Right_back_angle, STANDARD_ANGLES_LOCUST["back_body"]))
    scores["Body_Bone"] = round((LEFT_back_score + Right_back_score) / 2, 2)

    # Leg??-?-?????
    Left_leg_angle = calculate_angle(P(landmarks, LEFT_HIP), P(landmarks, LEFT_KNEE), P(landmarks, LEFT_ANKLE))
    Right_leg_angle = calculate_angle(P(landmarks, RIGHT_HIP), P(landmarks, RIGHT_KNEE), P(landmarks, RIGHT_ANKLE))
    LEFT_leg_score = (score_with_tolerance(Left_leg_angle, STANDARD_ANGLES_LOCUST["leg_straight"]))
    Right_leg_score = (score_with_tolerance(Right_leg_angle, STANDARD_ANGLES_LOCUST["leg_straight"]))
    scores["Knee_Bone"] = round((LEFT_leg_score + Right_leg_score) / 2, 2)

    # Arm??-?-?????
    Left_arm_angle = calculate_angle(P(landmarks, LEFT_ELBOW), P(landmarks, LEFT_SHOULDER), P(landmarks, LEFT_HIP))
    Right_arm_angle = calculate_angle(P(landmarks, RIGHT_ELBOW), P(landmarks, RIGHT_SHOULDER), P(landmarks, RIGHT_HIP))
    Left_armpit_score = (score_with_tolerance(Left_arm_angle, STANDARD_ANGLES_LOCUST["armpit"]))
    Right_armpit_score = (score_with_tolerance(Right_arm_angle, STANDARD_ANGLES_LOCUST["armpit"]))
    scores["Armpit_Bone"] = round((Left_armpit_score + Right_armpit_score) / 2, 2)

    # Head??-?-?????????
    Left_upper_body = calculate_angle(P(landmarks, NOSE), P(landmarks, LEFT_SHOULDER), P(landmarks, LEFT_HIP))
    Right_upper_body = calculate_angle(P(landmarks, NOSE), P(landmarks, RIGHT_SHOULDER), P(landmarks, RIGHT_HIP))
    Left_upper_body_score = (score_with_tolerance(Left_upper_body, STANDARD_ANGLES_LOCUST["upper_body"]))
    Right_upper_body_score = (score_with_tolerance(Right_upper_body, STANDARD_ANGLES_LOCUST["upper_body"]))
    scores["Head_Bone"] = round((Left_upper_body_score + Right_upper_body_score) / 2, 2)

    # ???
    scores["average_score"] = round(sum(scores.values()) / len(scores), 2)
    
    return scores