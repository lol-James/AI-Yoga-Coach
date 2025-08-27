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

# è¨­å??æ¨?æº?è§?åº¦è??ç¶?è¨?ç®?å¾???°ç??å¹³å??è§?åº?
STANDARD_ANGLES = {
    "arm": {"target": 180, "avg": 174},
    "body": {"target": 180, "avg": 167},
    "triangle": {"target": 90, "avg": 85}
}

TOLERANCE = 5  # å®¹è¨±ç¯???? Â±5 åº?
POWER = 1.5

def score_with_tolerance(actual_angle, angle_info):
    diff = abs(actual_angle - angle_info["avg"])
    if diff < 5:
        return 100
    elif 5 <= diff <= 50:   # ??¹ç??50åº?
        return round(100 * (1 - ((diff - TOLERANCE) / (50 - TOLERANCE)) ** POWER), 2)
    else:
        return 0

def evaluate_plank_pose(landmarks):
    def get_point(index):
        return [landmarks[index].x, landmarks[index].y]

    LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
    LEFT_ELBOW, RIGHT_ELBOW = 13, 14
    LEFT_WRIST, RIGHT_WRIST = 15, 16
    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_ANKLE, RIGHT_ANKLE = 27, 28

    scores = {}

    # Angle1ï¼????-???-???
    left_arm_angle = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_ELBOW), get_point(LEFT_WRIST))
    right_arm_angle = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_ELBOW), get_point(RIGHT_WRIST))
    left_score = score_with_tolerance(left_arm_angle, STANDARD_ANGLES["arm"]) if get_point(LEFT_WRIST)[1] > get_point(LEFT_SHOULDER)[1] else 0
    right_score = score_with_tolerance(right_arm_angle, STANDARD_ANGLES["arm"]) if get_point(RIGHT_WRIST)[1] > get_point(RIGHT_SHOULDER)[1] else 0
    scores["Arm Vertical"] = round((left_score + right_score) / 2, 2)

    # Angle2ï¼????-???-è¸?
    left_body_angle = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_HIP), get_point(LEFT_ANKLE))
    right_body_angle = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_HIP), get_point(RIGHT_ANKLE))
    body_score_left = score_with_tolerance(left_body_angle, STANDARD_ANGLES["body"])
    body_score_right = score_with_tolerance(right_body_angle, STANDARD_ANGLES["body"])
    scores["Body Alignment"] = round((body_score_left + body_score_right) / 2, 2)

    # Angle3ï¼????-???-è¸?
    left_triangle_angle = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_WRIST), get_point(LEFT_ANKLE))
    right_triangle_angle = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_WRIST), get_point(RIGHT_ANKLE))
    tri_score_left = score_with_tolerance(left_triangle_angle, STANDARD_ANGLES["triangle"])
    tri_score_right = score_with_tolerance(right_triangle_angle, STANDARD_ANGLES["triangle"])
    scores["Triangle Angle"] = round((tri_score_left + tri_score_right) / 2, 2)

    # Average
    avg_score = round(sum(scores.values()) / len(scores), 2)
    scores["average_score"] = avg_score

    return scores

if __name__ == '__main__':
    IMAGE_DIR = "plank/image"

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
                score = evaluate_plank_pose(results.pose_landmarks.landmark)
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
plank_0187.jpg -- 87.22
plank_0202.jpg -- 87.83
plank_0507.jpg -- 87.63
plank_0700.jpg -- 88.23
''' 