import os
import cv2
import numpy as np
import mediapipe as mp

mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    """Calculate angle between three points."""
    if None in (a, b, c):
        return None
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def score_with_tolerance(actual_angle, target_angle, tolerance=5, power=2):
    """Calculate score based on deviation from target angle."""
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
    """Evaluate Warrior 3 pose using standardized bone keys."""
    
    def get_point(index):
        """Helper to get landmark coordinates."""
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

    # ---------------------------------------------------------
    # 1. Arm Bone Evaluation (Standard Key: Arm_Bone)
    # ---------------------------------------------------------
    arm_left_angle = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_ELBOW), get_point(LEFT_WRIST))
    arm_right_angle = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_ELBOW), get_point(RIGHT_WRIST))
    
    arm_scores = []
    if arm_left_angle is not None:
        arm_scores.append(score_with_tolerance(arm_left_angle, 167.88))
    if arm_right_angle is not None:
        arm_scores.append(score_with_tolerance(arm_right_angle, 167.88))
    
    # Set standardized key for visualizer
    scores['Arm_Bone'] = round(sum(arm_scores)/len(arm_scores), 2) if arm_scores else 0

    # ---------------------------------------------------------
    # 2. Hip Bone Evaluation (Standard Key: Hip_Bone)
    # ---------------------------------------------------------
    left_hip_angle = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_HIP), get_point(LEFT_KNEE))
    right_hip_angle = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_HIP), get_point(RIGHT_KNEE))
    
    hip_score_left = 0
    hip_score_right = 0

    # Logic to determine which leg is lifted vs standing
    if left_hip_angle is not None and right_hip_angle is not None:
        # Compare deviation from 180 (straight line) to identify lifted leg
        if abs(left_hip_angle - 180) < abs(right_hip_angle - 180):
            scores['lifted_leg'] = 'Left' # Internal key for feedback logic
            hip_score_left = score_with_tolerance(left_hip_angle, 169.73) # Lifted target
            hip_score_right = score_with_tolerance(right_hip_angle, 97.04) # Standing target
        else:
            scores['lifted_leg'] = 'Right' # Internal key for feedback logic
            hip_score_left = score_with_tolerance(left_hip_angle, 97.04) # Standing target
            hip_score_right = score_with_tolerance(right_hip_angle, 169.73) # Lifted target
    else:
        scores['lifted_leg'] = None

    # Keep specific keys for detailed feedback generation
    scores['Hip_Bone_Left'] = hip_score_left
    scores['Hip_Bone_Right'] = hip_score_right

    # Set standardized key for visualizer (Average of both hips)
    scores['Hip_Bone'] = round((hip_score_left + hip_score_right) / 2, 2)

    # ---------------------------------------------------------
    # 3. Knee Bone Evaluation (Standard Key: Knee_Bone)
    # ---------------------------------------------------------
    leg_left_angle = calculate_angle(get_point(LEFT_HIP), get_point(LEFT_KNEE), get_point(LEFT_ANKLE))
    leg_right_angle = calculate_angle(get_point(RIGHT_HIP), get_point(RIGHT_KNEE), get_point(RIGHT_ANKLE))
    
    knee_score_left = score_with_tolerance(leg_left_angle, 172.48) if leg_left_angle is not None else 0
    knee_score_right = score_with_tolerance(leg_right_angle, 172.48) if leg_right_angle is not None else 0

    # Internal keys if needed for specific feedback
    scores['Knee_Bone_Left'] = knee_score_left
    scores['Knee_Bone_Right'] = knee_score_right

    # Set standardized key for visualizer (Average of both knees)
    scores['Knee_Bone'] = round((knee_score_left + knee_score_right) / 2, 2)

    # ---------------------------------------------------------
    # 4. Overall Score
    # ---------------------------------------------------------
    # Average of the 3 main standardized components
    avg_score = round((scores['Arm_Bone'] + scores['Hip_Bone'] + scores['Knee_Bone']) / 3, 2)
    scores['average_score'] = avg_score

    return scores