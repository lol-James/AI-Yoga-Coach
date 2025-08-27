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

# è§?åº¦å¹³?????? (??¹æ??ä½????çµ±è??è³????)
STANDARD_ANGLES = {
    "arm_straight": {"avg": 173, "label": "Arm Straight"},
    "arm_body": {"avg": 99, "label": "Arm-Body Angle"},
    "front_knee": {"avg": 114, "label": "Front Knee"},
    "back_knee": {"avg": 174, "label": "Back Knee"}
}

TOLERANCE = 5
POWER = 2

def score_with_tolerance(actual_angle, angle_info):
    diff = abs(actual_angle - angle_info["avg"])
    if diff < 5:
        return 100
    elif 5 <= diff <= 50:   
        return round(100 * (1 - ((diff - TOLERANCE) / (50 - TOLERANCE)) ** POWER), 2)
    else:
        return 0

def evaluate_warrior2_pose(landmarks):
    def get_point(index):
        return [landmarks[index].x, landmarks[index].y]

    # Landmark index å¸¸æ??
    LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
    LEFT_ELBOW, RIGHT_ELBOW = 13, 14
    LEFT_WRIST, RIGHT_WRIST = 15, 16
    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_KNEE, RIGHT_KNEE = 25, 26
    LEFT_ANKLE, RIGHT_ANKLE = 27, 28

    scores = {}

    # (1) ??? - ??? - ???ï¼???????ä¼¸ç?´ï??
    left_arm_angle = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_ELBOW), get_point(LEFT_WRIST))
    right_arm_angle = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_ELBOW), get_point(RIGHT_WRIST))
    left_arm_score = round(score_with_tolerance(left_arm_angle, STANDARD_ANGLES["arm_straight"]), 2)
    right_arm_score = round(score_with_tolerance(right_arm_angle, STANDARD_ANGLES["arm_straight"]), 2)
    scores["arm_score"] = round((left_arm_score + right_arm_score) / 2, )
    
    # (2) ??? - ??? - ???ï¼??????????èº«é???????´è??ï¼?
    left_arm_body_angle = calculate_angle(get_point(LEFT_WRIST), get_point(LEFT_SHOULDER), get_point(LEFT_HIP))
    right_arm_body_angle = calculate_angle(get_point(RIGHT_WRIST), get_point(RIGHT_SHOULDER), get_point(RIGHT_HIP))
    left_arm_body_score = round(score_with_tolerance(left_arm_body_angle, STANDARD_ANGLES["arm_body"]), 2)
    right_arm_body_score = round(score_with_tolerance(right_arm_body_angle, STANDARD_ANGLES["arm_body"]), 2)
    scores["arm_body_score"] = round((left_arm_body_score + right_arm_body_score) / 2, 2)

    # (3) ?????? vs å¾???³ï?????è¼???¥è?? 90 åº¦è????ºå?????
    left_knee_angle = calculate_angle(get_point(LEFT_HIP), get_point(LEFT_KNEE), get_point(LEFT_ANKLE))
    right_knee_angle = calculate_angle(get_point(RIGHT_HIP), get_point(RIGHT_KNEE), get_point(RIGHT_ANKLE))

    if abs(left_knee_angle - 90) < abs(right_knee_angle - 90):
        front_knee_angle = left_knee_angle
        back_knee_angle = right_knee_angle
        front_label, back_label = "Left", "Right"
    else:
        front_knee_angle = right_knee_angle
        back_knee_angle = left_knee_angle
        front_label, back_label = "Right", "Left"

    scores[f"{front_label} Leg Front Knee"] = round(score_with_tolerance(front_knee_angle, STANDARD_ANGLES["front_knee"]), 2)
    scores[f"{back_label} Leg Back Knee"] = round(score_with_tolerance(back_knee_angle, STANDARD_ANGLES["back_knee"]), 2)

    # å¹³å????????
    avg_score = round(sum(scores.values()) / len(scores), 2)
    scores["average_score"] = avg_score

    return scores
        
if __name__ == '__main__':
    IMAGE_DIR = "warrior_2/image"

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)

    min_score = 100
    min_score_file_name = ''
    low_score_images = []

    for filename in os.listdir(IMAGE_DIR):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(IMAGE_DIR, filename)
            print(f"Evaluating image: {filename}")

            image = cv2.imread(image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                score = evaluate_warrior2_pose(results.pose_landmarks.landmark)
                print(score)

                if score["average_score"] < 90:
                    low_score_images.append((filename, score["average_score"]))

                print(f"Average Score: {score['average_score']}\n")
            else:
                print("Pose landmarks not detected")

    # ??°å?ºæ?????ä½??????????
    print("Images with score below 90:")
    for fname, score in low_score_images:
        print(f"{fname} -- {score}")

    pose.close()


'''
Images with score below 90:
warrior2_0020.jpg -- 75.0
warrior2_0022.jpg -- 85.18
warrior2_0076.jpg -- 84.68
warrior2_0081.jpg -- 74.89
warrior2_0112.jpg -- 85.18
warrior2_0135.jpg -- 74.37
warrior2_0154.jpg -- 81.46
warrior2_0171.jpg -- 77.81
warrior2_0211.jpg -- 78.81
warrior2_0300.jpg -- 86.82
warrior2_0347.jpg -- 85.58
warrior2_0352.jpg -- 85.88
warrior2_0365.jpg -- 74.7
warrior2_0392.jpg -- 82.05
warrior2_0415.jpg -- 86.61
warrior2_0419.jpg -- 84.76
warrior2_0441.jpg -- 79.07
warrior2_0499.jpg -- 89.3
warrior2_0504.jpg -- 87.32
warrior2_0532.jpg -- 75.07
warrior2_0553.jpg -- 79.07
warrior2_0560.jpg -- 85.87
warrior2_0611.jpg -- 77.81
warrior2_0623.jpg -- 86.95
warrior2_0635.jpg -- 83.7
warrior2_0678.jpg -- 74.37
warrior2_0697.jpg -- 84.35
warrior2_0709.jpg -- 86.61
warrior2_0765.jpg -- 86.87
warrior2_0766.jpg -- 76.38
'''