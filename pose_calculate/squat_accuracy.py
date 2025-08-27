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
    if denom == 0:
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
    "Leg":      { "avg": 115.99},
    "BackLow":  { "avg": 113.49},
    "BackMid":  { "avg": 162.57},
    "BackHigh": { "avg": 164.55},
}

# 取點
def P(landmarks, i):
    return [landmarks[i].x, landmarks[i].y]

# Mediapipe 左右索引
L = {"shoulder":11, "elbow":13, "hip":23, "knee":25, "ankle":27, "ear":7}
R = {"shoulder":12, "elbow":14, "hip":24, "knee":26, "ankle":28, "ear":8}


def evaluate_squat_pose(landmarks):
    scores = {}

    # Leg：髖-膝-踝
    leg_L = calculate_angle(P(landmarks, L["hip"]), P(landmarks, L["knee"]), P(landmarks, L["ankle"]))
    leg_R = calculate_angle(P(landmarks, R["hip"]), P(landmarks, R["knee"]), P(landmarks, R["ankle"]))
    leg_score = (score_with_tolerance(leg_L, STANDARD_ANGLES_SQUAT["Leg"]) +
                 score_with_tolerance(leg_R, STANDARD_ANGLES_SQUAT["Leg"])) / 2
    scores["Leg"] = round(leg_score, 2)

    # BackLow：肩-髖-膝
    bl_L = calculate_angle(P(landmarks, L["shoulder"]), P(landmarks, L["hip"]), P(landmarks, L["knee"]))
    bl_R = calculate_angle(P(landmarks, R["shoulder"]), P(landmarks, R["hip"]), P(landmarks, R["knee"]))
    bl_score = (score_with_tolerance(bl_L, STANDARD_ANGLES_SQUAT["BackLow"]) +
                score_with_tolerance(bl_R, STANDARD_ANGLES_SQUAT["BackLow"])) / 2
    scores["BackLow"] = round(bl_score, 2)

    # BackMid：肘-肩-髖
    bm_L = calculate_angle(P(landmarks, L["elbow"]), P(landmarks, L["shoulder"]), P(landmarks, L["hip"]))
    bm_R = calculate_angle(P(landmarks, R["elbow"]), P(landmarks, R["shoulder"]), P(landmarks, R["hip"]))
    bm_score = (score_with_tolerance(bm_L, STANDARD_ANGLES_SQUAT["BackMid"]) +
                score_with_tolerance(bm_R, STANDARD_ANGLES_SQUAT["BackMid"])) / 2
    scores["BackMid"] = round(bm_score, 2)

    # BackHigh：耳-肩-髖
    bh_L = calculate_angle(P(landmarks, L["ear"]), P(landmarks, L["shoulder"]), P(landmarks, L["hip"]))
    bh_R = calculate_angle(P(landmarks, R["ear"]), P(landmarks, R["shoulder"]), P(landmarks, R["hip"]))
    bh_score = (score_with_tolerance(bh_L, STANDARD_ANGLES_SQUAT["BackHigh"]) +
                score_with_tolerance(bh_R, STANDARD_ANGLES_SQUAT["BackHigh"])) / 2
    scores["BackHigh"] = round(bh_score, 2)

    scores["average_score"] = round(sum(scores.values()) / len(scores), 2)
    return scores

