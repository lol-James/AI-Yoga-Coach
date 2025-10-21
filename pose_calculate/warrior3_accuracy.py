import os
import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    if None in (a, b, c):
        return None
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)


def score_with_tolerance(actual_angle, target_angle, tolerance=5, power=2):
    if actual_angle is None:
        return None
    diff = abs(actual_angle - target_angle)
    if diff <= tolerance:
        return 100
    elif diff <= 50:
        return round(100 * (1 - ((diff - tolerance) / (50 - tolerance)) ** power), 2)
    else:
        return 0


def evaluate_warrior3_pose(landmarks):
    """Evaluate Warrior 3 pose with separate left/right hip and knee scores."""
    def get_point(index):
        if landmarks[index].visibility < 0.5:
            return None
        return [landmarks[index].x, landmarks[index].y]

    # Mediapipe indices
    LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
    LEFT_ELBOW, RIGHT_ELBOW = 13, 14
    LEFT_WRIST, RIGHT_WRIST = 15, 16
    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_KNEE, RIGHT_KNEE = 25, 26
    LEFT_ANKLE, RIGHT_ANKLE = 27, 28

    scores = {}

    # Arm straightness
    arm_left_angle = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_ELBOW), get_point(LEFT_WRIST))
    arm_right_angle = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_ELBOW), get_point(RIGHT_WRIST))
    arm_scores = []
    if arm_left_angle is not None:
        arm_scores.append(score_with_tolerance(arm_left_angle, 167.88))
    if arm_right_angle is not None:
        arm_scores.append(score_with_tolerance(arm_right_angle, 167.88))
    scores['Arm_Bone'] = round(sum(arm_scores)/len(arm_scores), 2) if arm_scores else 0

    # Hip angles (left/right)
    left_hip_angle = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_HIP), get_point(LEFT_KNEE))
    right_hip_angle = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_HIP), get_point(RIGHT_KNEE))

    # Determine targets based on which side is straight (180) vs bent (~90)
    if left_hip_angle is not None and right_hip_angle is not None:
        if abs(left_hip_angle - 180) < abs(right_hip_angle - 180):
            scores['Hip_Bone_Left'] = score_with_tolerance(left_hip_angle, 169.73)  # straight
            scores['Hip_Bone_Right'] = score_with_tolerance(right_hip_angle, 97.04)  # bent
        else:
            scores['Hip_Bone_Left'] = score_with_tolerance(left_hip_angle, 97.04)  # bent
            scores['Hip_Bone_Right'] = score_with_tolerance(right_hip_angle, 169.73)  # straight
    else:
        scores['Hip_Bone_Left'] = 0
        scores['Hip_Bone_Right'] = 0

    # Knee straightness
    leg_left_angle = calculate_angle(get_point(LEFT_HIP), get_point(LEFT_KNEE), get_point(LEFT_ANKLE))
    leg_right_angle = calculate_angle(get_point(RIGHT_HIP), get_point(RIGHT_KNEE), get_point(RIGHT_ANKLE))
    scores['Knee_Bone_Left'] = score_with_tolerance(leg_left_angle, 172.48) if leg_left_angle is not None else 0
    scores['Knee_Bone_Right'] = score_with_tolerance(leg_right_angle, 172.48) if leg_right_angle is not None else 0
    scores['Knee_Bone'] = round((scores['Knee_Bone_Left'] + scores['Knee_Bone_Right']) / 2, 2)

    # Average score
    avg_score = round((scores['Arm_Bone'] + scores['Hip_Bone_Left'] + scores['Hip_Bone_Right'] + scores['Knee_Bone']) / 4, 2)
    scores['average_score'] = avg_score

    return scores