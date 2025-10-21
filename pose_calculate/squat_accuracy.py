import os
import cv2
import numpy as np
import mediapipe as mp

# ---------- 共用工具 ----------
def calculate_angle(a, b, c):
    a, b, c = np.array(a, dtype=float), np.array(b, dtype=float), np.array(c, dtype=float)
    ba = a - b
    bc = c - b
    denom = (np.linalg.norm(ba) * np.linalg.norm(bc))
    if denom < 1e-6:
        return 0.0
    cosine_angle = np.dot(ba, bc) / denom
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return float(np.degrees(angle))

TOLERANCE = 5
POWER = 2

def score_with_tolerance(actual_angle, angle_info):
    diff = abs(actual_angle - angle_info["avg"])  # 依你原本邏輯使用 avg
    if diff < 5:
        return 100.0
    elif 5 <= diff <= 50:
        return round(100 * (1 - ((diff - TOLERANCE) / (50 - TOLERANCE)) ** POWER), 2)
    else:
        return 0.0


# ---------- Squat 標準角度（依你提供的 avg） ----------
STANDARD_ANGLES_SQUAT = {
    "leg_curve":      { "avg": 115.99},
    "butt_curve":  { "avg": 113.49},
    "arm_straight":  { "avg": 162.57},
    "body_straight": { "avg": 164.55},
}

# 取點
def evaluate_squat_pose(landmarks):
    def P(landmarks, i):
        return [landmarks[i].x, landmarks[i].y]

    LEFT_EAR, RIGHT_EAR = 7, 8
    LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
    LEFT_ELBOW, RIGHT_ELBOW = 13, 14
    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_KNEE, RIGHT_KNEE = 25, 26
    LEFT_ANKLE, RIGHT_ANKLE = 27, 28

    scores = {}

    # Leg：髖-膝-踝
    Left_leg_angle = calculate_angle(P(landmarks, LEFT_HIP), P(landmarks, LEFT_KNEE), P(landmarks, LEFT_ANKLE))
    Right_leg_angle = calculate_angle(P(landmarks, RIGHT_HIP), P(landmarks, RIGHT_KNEE), P(landmarks, RIGHT_ANKLE))
    LEFT_leg_score = (score_with_tolerance(Left_leg_angle, STANDARD_ANGLES_SQUAT["leg_curve"]))
    Right_leg_score = (score_with_tolerance(Right_leg_angle, STANDARD_ANGLES_SQUAT["leg_curve"]))
    scores["Knee_Bone"] = round((LEFT_leg_score + Right_leg_score) / 2, 2)

    # BackLow：肩-髖-膝
    Left_butt_angle = calculate_angle(P(landmarks, LEFT_SHOULDER), P(landmarks, LEFT_HIP), P(landmarks, LEFT_KNEE))
    Right_butt_angle = calculate_angle(P(landmarks, RIGHT_SHOULDER), P(landmarks, RIGHT_HIP), P(landmarks, RIGHT_KNEE))
    LEFT_butt_score = (score_with_tolerance(Left_butt_angle, STANDARD_ANGLES_SQUAT["butt_curve"]))
    Right_butt_score = (score_with_tolerance(Right_butt_angle, STANDARD_ANGLES_SQUAT["butt_curve"]))
    scores["Hip_Bone"] = round((LEFT_butt_score + Right_butt_score) / 2, 2)

    # BackMid：肘-肩-髖
    Left_arm_angle = calculate_angle(P(landmarks, LEFT_ELBOW), P(landmarks, LEFT_SHOULDER), P(landmarks, LEFT_HIP))
    Right_arm_angle = calculate_angle(P(landmarks,RIGHT_ELBOW), P(landmarks, RIGHT_SHOULDER), P(landmarks, RIGHT_HIP))
    LEFT_arm_score = (score_with_tolerance(Left_arm_angle, STANDARD_ANGLES_SQUAT["arm_straight"]))
    Right_arm_score = (score_with_tolerance(Right_arm_angle, STANDARD_ANGLES_SQUAT["arm_straight"]))
    scores["Armpit_Bone"] = round((LEFT_arm_score + Right_arm_score) / 2, 2)

    # BackHigh：耳-肩-髖
    Left_body_angle = calculate_angle(P(landmarks, LEFT_EAR), P(landmarks, LEFT_SHOULDER), P(landmarks, LEFT_HIP))
    Right_body_angle = calculate_angle(P(landmarks, RIGHT_EAR), P(landmarks, RIGHT_SHOULDER), P(landmarks, RIGHT_HIP))
    LEFT_body_score = (score_with_tolerance(Left_body_angle, STANDARD_ANGLES_SQUAT["body_straight"]))
    Right_body_score = (score_with_tolerance(Right_body_angle, STANDARD_ANGLES_SQUAT["body_straight"]))
    scores["Upperbody_Bone"] = round((LEFT_body_score + Right_body_score) / 2, 2)

    scores["average_score"] = round(sum(scores.values()) / len(scores), 2)
    return scores