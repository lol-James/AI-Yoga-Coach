import os
import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path

# 參數設定
TOLERANCE = 5
POWER = 1.5
MAX_DIFF = 50

# 標準角度
STANDARD_ANGLES = {
    "arm": {"avg": 166.01, "label": "Arm"},
    "torso": {"avg": 75.33, "label": "Torso"},
    "leg": {"avg": 174.93, "label": "Leg"}
}

# Mediapipe 初始化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

# ----- 工具函式 -----
def calculate_angle(a, b, c):
    if None in (a, b, c): return None
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return round(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))), 2)

def calculate_score(diff):  
    if diff <= TOLERANCE: return 100.0
    if diff >= MAX_DIFF: return 0.0
    return round(100 * (1 - ((diff - TOLERANCE)/(MAX_DIFF - TOLERANCE))**POWER), 2)

def get_landmarks(image):
    h, w, _ = image.shape
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)
    if not results.pose_landmarks:
        return None
    lm = results.pose_landmarks.landmark
    return [(int(p.x * w), int(p.y * h)) if p.visibility > 0.5 else None for p in lm] + [None] * (33 - len(lm))

def evaluate_downward_facing_dog_pose(landmarks):
    if hasattr(landmarks[0], "x") and hasattr(landmarks[0], "y"):
        converted = []
        for p in landmarks:
            if getattr(p, "visibility", 1.0) > 0.5:
                converted.append((float(p.x), float(p.y)))  # 用 normalized xy 即可
            else:
                converted.append(None)
        landmarks = converted
    left_ids = [11, 13, 15, 23, 25, 27]
    right_ids = [12, 14, 16, 24, 26, 28]
    def valid(ids): return all(landmarks[i] is not None for i in ids)

    # 因對稱，故先判斷左右是否都存在，否則只計算存在的那邊
    used = None
    if valid(left_ids) and valid(right_ids):
        used = "both"
    elif valid(left_ids):
        used = "left"
    elif valid(right_ids):
        used = "right"
    else:
        return

    # arm: 手臂   torso: 軀幹   leg: 下肢
    if used == "both":
        arm = (calculate_angle(landmarks[11], landmarks[13], landmarks[15]) + calculate_angle(landmarks[12], landmarks[14], landmarks[16])) / 2
        torso = (calculate_angle(landmarks[11], landmarks[23], landmarks[25]) + calculate_angle(landmarks[12], landmarks[24], landmarks[26])) / 2
        leg = (calculate_angle(landmarks[23], landmarks[25], landmarks[27]) + calculate_angle(landmarks[24], landmarks[26], landmarks[28])) / 2
    elif used == "left":
        arm = calculate_angle(landmarks[11], landmarks[13], landmarks[15])
        torso = calculate_angle(landmarks[11], landmarks[23], landmarks[25])
        leg = calculate_angle(landmarks[23], landmarks[25], landmarks[27])
    else:
        arm = calculate_angle(landmarks[12], landmarks[14], landmarks[16])
        torso = calculate_angle(landmarks[12], landmarks[24], landmarks[26])
        leg = calculate_angle(landmarks[24], landmarks[26], landmarks[28])

    if None in (arm, torso, leg):
        return

    # 角度差與分數
    diffs = {
        "arm": abs(arm - STANDARD_ANGLES["arm"]["avg"]),
        "torso": abs(torso - STANDARD_ANGLES["torso"]["avg"]),
        "leg": abs(leg - STANDARD_ANGLES["leg"]["avg"])
    }
    scores1 = {k: calculate_score(d) if d is not None else None for k, d in diffs.items()}
    scores = round(np.nanmean([s for s in scores1.values() if s is not None]), 2)

    return scores
