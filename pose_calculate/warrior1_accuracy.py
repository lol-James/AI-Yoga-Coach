import os
import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path

# ?????¸è¨­å®? 
TOLERANCE = 5  
POWER = 1.5      
MAX_DIFF = 50    

# æ¨?æº?è§?åº?
STANDARD_ANGLES = {
    "front_leg": 109.43,
    "back_leg": 171.03,
    "front_leg_trunk": 113.09,
    "arm": 167.86,
    "arm_trunk": 168.97
}

# è³????å¤¾è¨­å®?
input_folder = "warrior_1"
output_folder = "warrior_1_annotated(nonlinear)"
os.makedirs(output_folder, exist_ok=True)

# Mediapipe ???å§????
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)

# ----- å·¥å?·å?½å?? -----
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

def evaluate_warrior1_pose(landmarks):
        # ??¿é?¨è??åº?
    L_leg = calculate_angle(landmarks[23], landmarks[25], landmarks[27])
    R_leg = calculate_angle(landmarks[24], landmarks[26], landmarks[28])
    if None in (L_leg, R_leg): 
        return
    # ??¤å?????å¾????
    if L_leg < R_leg:
        front_leg, back_leg = L_leg, R_leg
        front_leg_trunk = (11,23,25) if all(landmarks[i] for i in (11,23,25)) else None
    else:
        front_leg, back_leg = R_leg, L_leg
        front_leg_trunk = (12,24,26) if all(landmarks[i] for i in (12,24,26)) else None

    leg_trunk = calculate_angle(landmarks[front_leg_trunk[0]], landmarks[front_leg_trunk[1]], landmarks[front_leg_trunk[2]]) if front_leg_trunk else None

    # ???????????©è??è§?åº?
    LA1 = calculate_angle(landmarks[23], landmarks[11], landmarks[13])
    LA2 = calculate_angle(landmarks[11], landmarks[13], landmarks[15])
    RA1 = calculate_angle(landmarks[24], landmarks[12], landmarks[14])
    RA2 = calculate_angle(landmarks[12], landmarks[14], landmarks[16])
    arm_avg = np.nanmean([a for a in (LA2, RA2) if a is not None]) if (LA2 or RA2) else None
    arm_trunk_avg = np.nanmean([a for a in (LA1, RA1) if a is not None]) if (LA1 or RA1) else None

    
    diffs = {
        "front_leg": abs(front_leg - STANDARD_ANGLES["front_leg"]),
        "back_leg": abs(back_leg  - STANDARD_ANGLES["back_leg"]),
        "leg_trunk": abs((leg_trunk or 0) - STANDARD_ANGLES["front_leg_trunk"]) if leg_trunk is not None else None,
        "arm": abs((arm_avg or 0) - STANDARD_ANGLES["arm"]) if arm_avg is not None else None,
        "arm_trunk": abs((arm_trunk_avg or 0) - STANDARD_ANGLES["arm_trunk"]) if arm_trunk_avg is not None else None
    }
    scores = {k: calculate_score(d) if d is not None else None for k, d in diffs.items()}
    avg_score = round(np.nanmean([s for s in scores.values() if s is not None]), 2)

    return avg_score

# ----- ä¸»ç??å¼? -----
if __name__ == '__main__':
    for img_file in sorted(Path(input_folder).glob("*.jpg")):
        img = cv2.imread(str(img_file))
        landmarks = get_landmarks(img)
        if not landmarks:
            continue
        
        txts = evaluate_warrior1_pose(landmarks)
        print(txts)

    pose.close()
