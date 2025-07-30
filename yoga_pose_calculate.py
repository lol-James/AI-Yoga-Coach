import os
import cv2
import numpy as np
import mediapipe as mp
from tkinter import filedialog, Tk

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True)
mp_drawing = mp.solutions.drawing_utils

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def score_angle(diff, tolerance=5, power=2, max_diff=90):
    if diff > max_diff:
        return 0
    elif diff <= tolerance:
        return 100
    else:
        return 100 * (1 - ((diff - tolerance) / (max_diff - tolerance)) ** power)

def evaluate_pose(landmarks, pose_name, image=None):
    results = {}
    pose_data = POSE_DEFINITIONS.get(pose_name.lower())
    if not pose_data:
        print(f"未定義的姿勢: {pose_name}")
        return None

    tolerance = pose_data["params"]["tolerance"]
    power = pose_data["params"]["power"]
    max_diff = pose_data["params"]["max_diff"]

    valid_scores = []
    h, w = image.shape[:2] if image is not None else (1, 1)
    overlay_lines = []

    for name, (pts, std_angle) in pose_data["angles"].items():
        try:
            a, b, c = [landmarks[i] for i in pts]
            if any(v.visibility < 0.3 for v in [a, b, c]):
                continue
            pt = lambda lm: np.array([lm.x * w, lm.y * h])
            angle = calculate_angle(pt(a), pt(b), pt(c))
            diff = abs(angle - std_angle)
            score = score_angle(diff, tolerance=tolerance, power=power, max_diff=max_diff)
            results[name] = round(score, 2)
            valid_scores.append(score)
            overlay_lines.append(f"{name}: {round(score, 1)}")
        except:
            continue

    avg = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else 0
    results['average_score'] = avg
    if image is not None:
        overlay_lines.insert(0, f"Total: {avg}")
        for i, text in enumerate(overlay_lines):
            y = 30 + i * 25
            cv2.putText(
                image, text, (10, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA
            )
    return results

POSE_DEFINITIONS = {
    "bridge": {
        "params": {"tolerance": 5, "power": 2, "max_diff": 90},
        "angles": {
            "hip": ([11, 23, 25], 162.94),
            "knee": ([23, 25, 27], 67.88),
        },
    },
    "chair": {
        "params": {"tolerance": 5, "power": 2, "max_diff": 50},
        "angles": {
            "leg": ([23, 25, 27], 115.99),
            "back_low": ([11, 23, 25], 113.49),
            "back_mid": ([13, 11, 23], 162.57),
            "back_high": ([7, 11, 23], 164.55),
        },
    },
    "cow": {
        "params": {"tolerance": 5, "power": 2, "max_diff": 50},
        "angles": {
            "back": ([11, 23, 25], 122.68),
            "leg": ([23, 25, 27], 95.12),
            "arm": ([11, 13, 15], 170.06),
        },
    },
    "downward_facing_dog": {
        "params": {"tolerance": 5, "power": 1.5, "max_diff": 50},
        "angles": {
            "arm": ([11, 13, 15], 166.01),
            "torso": ([11, 23, 25], 75.33),
            "leg": ([23, 25, 27], 174.93),
        },
    },
    "locust": {
        "params": {"tolerance": 5, "power": 2, "max_diff": 50},
        "angles": {
            "back_low": ([11, 23, 25], 135.90),
            "leg": ([23, 25, 27], 159.37),
            "arm": ([13, 11, 23], 31.42),
            "head": ([0, 11, 23], 163.04),
        },
    },
    "plank": {
        "params": {"tolerance": 5, "power": 1.5, "max_diff": 50},
        "angles": {
            "arm": ([11, 13, 15], 174),
            "body": ([11, 23, 27], 167),
            "triangle": ([11, 15, 27], 85),
        },
    },
    "staff": {
        "params": {"tolerance": 5, "power": 2, "max_diff": 50},
        "angles": {
            "back": ([11, 23, 25], 110.1),
            "leg": ([23, 25, 27], 160.0),
        },
    },
    "triangle": {
        "params": {"tolerance": 5, "power": 2, "max_diff": 90},
        "angles": {
            "trunk": ([11, 0, 23], 74.74),
            "pelvis": ([23, 25, 24], 69.13),
            "shoulder": ([12, 14, 11], 170.59),
        },
    },
    "warrior1": {
        "params": {"tolerance": 5, "power": 1.5, "max_diff": 50},
        "angles": {
            "front_leg": ([23, 25, 27], 109.43),
            "back_leg": ([24, 26, 28], 171.03),
            "front_leg_trunk": ([11, 23, 25], 113.09),
            "arm": ([11, 13, 15], 167.86),
            "arm_trunk": ([23, 11, 13], 168.97),
        },
    },
    "warrior2": {
        "params": {"tolerance": 5, "power": 2, "max_diff": 50},
        "angles": {
            "arm": ([11, 13, 15], 173),
            "arm_body": ([15, 11, 23], 99),
            "front_knee": ([23, 25, 27], 114),
            "back_knee": ([24, 26, 28], 174),
        },
    },
}


def evaluate_and_display_pose(frame, pose_index, label_widget):
    import cv2
    import numpy as np
    import mediapipe as mp
    from PyQt5.QtGui import QFont

    # 原始 pose 名稱對應
    pose_map = {
        0: "downward_facing_dog",
        1: "warrior1",
        2: "warrior2",
        3: "cow",
        4: "plank",
        5: "staff",
        6: "chair",
        7: "locust",
        8: "triangle",
        9: "bridge",
    }

    # 美觀顯示用名稱（完整名稱）
    pose_display_name_map = {
        "downward_facing_dog": "Downward Facing Dog",
        "warrior1": "Warrior I",
        "warrior2": "Warrior II",
        "cow": "Cow Pose",
        "plank": "Plank Pose",
        "staff": "Staff Pose",
        "chair": "Chair Pose",
        "locust": "Locust Pose",
        "triangle": "Triangle Pose",
        "bridge": "Bridge Pose"
    }

    pose_name = pose_map.get(pose_index, None)
    if pose_name is None:
        return

    display_name = pose_display_name_map.get(pose_name, pose_name.title())

    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=False) as pose:
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image_rgb)

        if result.pose_landmarks:
            scores = evaluate_pose(result.pose_landmarks.landmark, pose_name)
            avg = scores.get('average_score', 0)

            # 文字內容
            text = f"{display_name} {avg:.1f}"

            # 動態調整字體大小（越長越小）
            font_size = 20  # 預設
            if len(text) > 20:
                font_size = 14
            elif len(text) > 15:
                font_size = 16
            elif len(text) > 10:
                font_size = 18

            font = QFont("Arial", font_size)
            label_widget.setFont(font)
            label_widget.setPlainText(text)

if __name__ == '__main__':
    pose_options = list(POSE_DEFINITIONS.keys())
    print("請選擇一個瑜珈姿勢：")
    for i, name in enumerate(pose_options, 1):
        print(f"{i}. {name}")

    try:
        choice = int(input("輸入數字（1-10）：").strip())
        pose_name = pose_options[choice - 1]
    except (ValueError, IndexError):
        print("輸入錯誤，請重新執行程式。")
        exit()

    Tk().withdraw()
    file_path = filedialog.askopenfilename(title="選擇一張圖片", filetypes=[["Image Files", "*.jpg *.png"]])
    if not file_path:
        print("未選擇圖片。")
        exit()

    image = cv2.imread(file_path)
    h, w, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = pose.process(image_rgb)

    if not result.pose_landmarks:
        print("無法偵測姿勢")
    else:
        mp_drawing.draw_landmarks(image, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        score_result = evaluate_pose(result.pose_landmarks.landmark, pose_name, image)
        print(f"{os.path.basename(file_path)} 的評分結果：")
        # 姿勢總分
        print(score_result)

        cv2.imshow("Pose Result", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    pose.close()
