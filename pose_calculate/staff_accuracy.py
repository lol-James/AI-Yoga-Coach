import os
import cv2
import numpy as np
import mediapipe as mp

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def score_with_tolerance(actual_angle, target_angle, tolerance=5, power=2):
    diff = abs(actual_angle - target_angle)
    if diff <= tolerance:
        return 100
    elif diff <= 50:
        return round(100 * (1 - ((diff - tolerance) / (50 - tolerance)) ** power), 2)
    else:
        return 0

def evaluate_staff_pose(landmarks):
    def get_point(index):
        return [landmarks[index].x, landmarks[index].y]

    LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_KNEE, RIGHT_KNEE = 25, 26
    LEFT_ANKLE, RIGHT_ANKLE = 27, 28

    # Staff pose æ¨?æº?è§?åº¦ï??ä¾???? main.pyï¼?
    STANDARD_ANGLES = {
        "Back": 110.1,
        "Leg": 160.0
    }

    scores = {}

    leg_left = calculate_angle(get_point(LEFT_HIP), get_point(LEFT_KNEE), get_point(LEFT_ANKLE))
    leg_right = calculate_angle(get_point(RIGHT_HIP), get_point(RIGHT_KNEE), get_point(RIGHT_ANKLE))
    back_left = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_HIP), get_point(LEFT_KNEE))
    back_right = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_HIP), get_point(RIGHT_KNEE))

    scores['Leg'] = round((score_with_tolerance(leg_left, STANDARD_ANGLES['Leg']) + score_with_tolerance(leg_right, STANDARD_ANGLES['Leg'])) / 2, 2)
    scores['Back'] = round((score_with_tolerance(back_left, STANDARD_ANGLES['Back']) + score_with_tolerance(back_right, STANDARD_ANGLES['Back'])) / 2, 2)

    avg_score = round(sum(scores.values()) / len(scores), 2)
    scores['average_score'] = avg_score

    return scores

if __name__ == '__main__':
    IMAGE_DIR = "staff_recognizable"

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)

    low_score_images = []

    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            path = os.path.join(IMAGE_DIR, filename)
            print(f"Evaluating: {filename}")

            image = cv2.imread(path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                score = evaluate_staff_pose(results.pose_landmarks.landmark)
                print(score)
                if score['average_score'] < 90:
                    low_score_images.append((filename, score['average_score']))
            else:
                print("Pose not detected")

    print("\nImages with score below 90:")
    for fname, sc in low_score_images:
        print(f"{fname} -- {sc}")

    pose.close()