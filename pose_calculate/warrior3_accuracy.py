import os
import cv2
import numpy as np
import mediapipe as mp
import matplotlib.pyplot as plt

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def calculate_angle(a, b, c):
    if None in (a, b, c):  # �???????�?缺失
        return None
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)


def score_with_tolerance(actual_angle, target_angle, tolerance=5, power=2):
    if actual_angle is None:  # �????�?度就�?�?
        return None
    diff = abs(actual_angle - target_angle)
    if diff <= tolerance:
        return 100
    elif diff <= 50:
        return round(100 * (1 - ((diff - tolerance) / (50 - tolerance)) ** power), 2)
    else:
        return 0


def evaluate_warrior3_pose(landmarks):
    def get_point(index):
        if landmarks[index].visibility < 0.5:  # ??��??度�??足就??��????????
            return None
        return [landmarks[index].x, landmarks[index].y]

    # Mediapipe �?�?索�??
    LEFT_SHOULDER, RIGHT_SHOULDER = 11, 12
    LEFT_ELBOW, RIGHT_ELBOW = 13, 14
    LEFT_WRIST, RIGHT_WRIST = 15, 16
    LEFT_HIP, RIGHT_HIP = 23, 24
    LEFT_KNEE, RIGHT_KNEE = 25, 26
    LEFT_ANKLE, RIGHT_ANKLE = 27, 28

    scores = {}

    # 1. ??????水平
    arm_left = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_ELBOW), get_point(LEFT_WRIST))
    arm_right = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_ELBOW), get_point(RIGHT_WRIST))

    arm_scores = []
    if arm_left is not None:
        arm_scores.append(score_with_tolerance(arm_left, 167.88))
    if arm_right is not None:
        arm_scores.append(score_with_tolerance(arm_right, 167.88))

    scores['Arm'] = round(sum(s for s in arm_scores if s is not None) / len(arm_scores), 2) if arm_scores else 0

    # 2. �?�? + 大�?? (??��????��????��?? 90 ??? 180)
    back_left = calculate_angle(get_point(LEFT_SHOULDER), get_point(LEFT_HIP), get_point(LEFT_KNEE))
    back_right = calculate_angle(get_point(RIGHT_SHOULDER), get_point(RIGHT_HIP), get_point(RIGHT_KNEE))

    if back_left is not None and back_right is not None:
        if abs(back_left - 90) < abs(back_left - 180):
            scores['Back Left'] = score_with_tolerance(back_left, 97.04)
            scores['Back Right'] = score_with_tolerance(back_right, 169.73)
        else:
            scores['Back Left'] = score_with_tolerance(back_left, 169.73)
            scores['Back Right'] = score_with_tolerance(back_right, 97.04)
        scores['Back'] = round((scores['Back Left'] + scores['Back Right']) / 2, 2)
    else:
        scores['Back'] = 0

    # 3. ?????�水�?
    leg_left = calculate_angle(get_point(LEFT_HIP), get_point(LEFT_KNEE), get_point(LEFT_ANKLE))
    leg_right = calculate_angle(get_point(RIGHT_HIP), get_point(RIGHT_KNEE), get_point(RIGHT_ANKLE))

    leg_scores = []
    if leg_left is not None:
        leg_scores.append(score_with_tolerance(leg_left, 172.48))
    if leg_right is not None:
        leg_scores.append(score_with_tolerance(leg_right, 172.48))

    scores['Leg'] = round(sum(s for s in leg_scores if s is not None) / len(leg_scores), 2) if leg_scores else 0

    # 平�????????
    valid_scores = [scores['Arm'], scores['Back'], scores['Leg']]
    avg_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else 0
    scores['average_score'] = avg_score

    return scores


if __name__ == '__main__':
    folder_path = r"C:\Users\User\Desktop\test"

    if not os.path.exists(folder_path):
        print("??��????��?????夾�??�?確�??路�????��?�正確�??")
        exit()

    with mp_pose.Pose(static_image_mode=True) as pose:
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                image_path = os.path.join(folder_path, filename)
                image = cv2.imread(image_path)
                if image is None:
                    continue
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                results = pose.process(image_rgb)

                if results.pose_landmarks:
                    scores = evaluate_warrior3_pose(results.pose_landmarks.landmark)
                    print(f"{filename} ?????��??�?�????:", scores)

                    # 繪製骨�?��???????��??
                    annotated_image = image_rgb.copy()
                    mp_drawing.draw_landmarks(
                        annotated_image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=2),
                    )

                    # ??��?????左�??�????�???????
                    text = f"Avg: {scores['average_score']} | Arm: {scores['Arm']} | Back: {scores['Back']} | Leg: {scores['Leg']}"
                    cv2.putText(annotated_image, text, (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)

                    # 顯示??????
                    plt.figure(figsize=(8, 8))
                    plt.imshow(annotated_image)
                    plt.axis("off")
                    plt.title(filename)
                    plt.show()
                else:
                    print(f"{filename} ??��????�測??�姿??��??")



