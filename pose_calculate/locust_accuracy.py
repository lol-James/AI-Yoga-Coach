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
    "BackLow": {"avg": 135.90},  # ªÓ-Æb-½¥
    "Leg":     {"avg": 159.37},  # Æb-½¥-½ï
    "Arm":     {"avg": 31.42},   # ¨y-ªÓ-Æb
    "Head":    {"avg": 163.04},  # »ó-ªÓ-Æb
}

def P(landmarks, i):
    return [landmarks[i].x, landmarks[i].y]

L = {"shoulder": 11, "elbow": 13, "hip": 23, "knee": 25, "ankle": 27}
R = {"shoulder": 12, "elbow": 14, "hip": 24, "knee": 26, "ankle": 28}
NOSE = 0

def evaluate_locust_pose(landmarks):
    scores = {}

    # BackLow¡GªÓ-Æb-½¥¡]¥ª¥k¡^
    bl_L = calculate_angle(P(landmarks, L["shoulder"]), P(landmarks, L["hip"]), P(landmarks, L["knee"]))
    bl_R = calculate_angle(P(landmarks, R["shoulder"]), P(landmarks, R["hip"]), P(landmarks, R["knee"]))
    bl_score = (
        score_with_tolerance(bl_L, STANDARD_ANGLES_LOCUST["BackLow"]) +
        score_with_tolerance(bl_R, STANDARD_ANGLES_LOCUST["BackLow"])
    ) / 2
    scores["BackLow"] = round(bl_score, 2)

    # Leg¡GÆb-½¥-½ï¡]¥ª¥k¡^
    leg_L = calculate_angle(P(landmarks, L["hip"]), P(landmarks, L["knee"]), P(landmarks, L["ankle"]))
    leg_R = calculate_angle(P(landmarks, R["hip"]), P(landmarks, R["knee"]), P(landmarks, R["ankle"]))
    leg_score = (
        score_with_tolerance(leg_L, STANDARD_ANGLES_LOCUST["Leg"]) +
        score_with_tolerance(leg_R, STANDARD_ANGLES_LOCUST["Leg"])
    ) / 2
    scores["Leg"] = round(leg_score, 2)

    # Arm¡G¨y-ªÓ-Æb¡]¥ª¥k¡^
    arm_L = calculate_angle(P(landmarks, L["elbow"]), P(landmarks, L["shoulder"]), P(landmarks, L["hip"]))
    arm_R = calculate_angle(P(landmarks, R["elbow"]), P(landmarks, R["shoulder"]), P(landmarks, R["hip"]))
    arm_score = (
        score_with_tolerance(arm_L, STANDARD_ANGLES_LOCUST["Arm"]) +
        score_with_tolerance(arm_R, STANDARD_ANGLES_LOCUST["Arm"])
    ) / 2
    scores["Arm"] = round(arm_score, 2)

    # Head¡G»ó-ªÓ-Æb¡]¥ª¥k¡F»ó¦@¥Î¡^
    head_L = calculate_angle(P(landmarks, NOSE), P(landmarks, L["shoulder"]), P(landmarks, L["hip"]))
    head_R = calculate_angle(P(landmarks, NOSE), P(landmarks, R["shoulder"]), P(landmarks, R["hip"]))
    head_score = (
        score_with_tolerance(head_L, STANDARD_ANGLES_LOCUST["Head"]) +
        score_with_tolerance(head_R, STANDARD_ANGLES_LOCUST["Head"])
    ) / 2
    scores["Head"] = round(head_score, 2)

    # ¥­§¡¤À
    scores["average_score"] = round(sum(scores.values()) / len(scores), 2)
    return scores
