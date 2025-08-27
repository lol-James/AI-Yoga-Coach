import cv2
import mediapipe as mp
import numpy as np

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba = a - b
    bc = c - b
    if np.linalg.norm(ba) == 0 or np.linalg.norm(bc) == 0:
        return None
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def score_angle(diff, weight=50, tolerance=5, power=2):
    if diff > 90:
        return 0
    elif diff <= tolerance:
        return weight
    else:
        return weight * (1 - ((diff - tolerance) / (90 - tolerance)) ** power)

def extract_angles(image_path, pose):
    image = cv2.imread(image_path)
    if image is None:
        print(f"圖片讀取失敗：{image_path}")
        return None, None

    h, w, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if not results.pose_landmarks:
        print("無偵測到姿勢")
        return None, None

    lm = results.pose_landmarks.landmark
    def pt(l): return (int(lm[l].x * w), int(lm[l].y * h))

    hip_angles = []
    knee_angles = []

    try:
        # 髖關節（左右）
        if all(lm[i].visibility > 0.5 for i in [mp.solutions.pose.PoseLandmark.LEFT_SHOULDER,
                                                mp.solutions.pose.PoseLandmark.LEFT_HIP,
                                                mp.solutions.pose.PoseLandmark.LEFT_KNEE]):
            hip_angles.append(calculate_angle(pt(mp.solutions.pose.PoseLandmark.LEFT_SHOULDER),
                                              pt(mp.solutions.pose.PoseLandmark.LEFT_HIP),
                                              pt(mp.solutions.pose.PoseLandmark.LEFT_KNEE)))
        if all(lm[i].visibility > 0.5 for i in [mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER,
                                                mp.solutions.pose.PoseLandmark.RIGHT_HIP,
                                                mp.solutions.pose.PoseLandmark.RIGHT_KNEE]):
            hip_angles.append(calculate_angle(pt(mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER),
                                              pt(mp.solutions.pose.PoseLandmark.RIGHT_HIP),
                                              pt(mp.solutions.pose.PoseLandmark.RIGHT_KNEE)))

        # 膝關節（左右）
        if all(lm[i].visibility > 0.5 for i in [mp.solutions.pose.PoseLandmark.LEFT_HIP,
                                                mp.solutions.pose.PoseLandmark.LEFT_KNEE,
                                                mp.solutions.pose.PoseLandmark.LEFT_ANKLE]):
            knee_angles.append(calculate_angle(pt(mp.solutions.pose.PoseLandmark.LEFT_HIP),
                                               pt(mp.solutions.pose.PoseLandmark.LEFT_KNEE),
                                               pt(mp.solutions.pose.PoseLandmark.LEFT_ANKLE)))
        if all(lm[i].visibility > 0.5 for i in [mp.solutions.pose.PoseLandmark.RIGHT_HIP,
                                                mp.solutions.pose.PoseLandmark.RIGHT_KNEE,
                                                mp.solutions.pose.PoseLandmark.RIGHT_ANKLE]):
            knee_angles.append(calculate_angle(pt(mp.solutions.pose.PoseLandmark.RIGHT_HIP),
                                               pt(mp.solutions.pose.PoseLandmark.RIGHT_KNEE),
                                               pt(mp.solutions.pose.PoseLandmark.RIGHT_ANKLE)))

        hip = np.mean([a for a in hip_angles if a is not None]) if hip_angles else None
        knee = np.mean([a for a in knee_angles if a is not None]) if knee_angles else None

        return hip, knee

    except Exception as e:
        print(f"分析失敗：{e}")
        return None, None


# ================= 新增：函式版（回傳 scores） =================
def evaluate_bridge_pose(landmarks, standard_hip=162.94, standard_knee=67.88, vis_thresh=0.5):
    """
    以 MediaPipe 的 landmarks 計算 Bridge 總分（髖/膝各 50 分）。
    回傳 scores，格式與其他演算法一致。
    """
    import numpy as np
    import mediapipe as mp

    def calculate_angle(a, b, c):
        a, b, c = np.array(a), np.array(b), np.array(c)
        ba = a - b
        bc = c - b
        if np.linalg.norm(ba) == 0 or np.linalg.norm(bc) == 0:
            return None
        cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine, -1.0, 1.0))
        return np.degrees(angle)

    def score_angle(diff, weight=50, tolerance=5, power=2):
        if diff > 90:
            return 0
        elif diff <= tolerance:
            return weight
        else:
            return weight * (1 - ((diff - tolerance) / (90 - tolerance)) ** power)

    P = mp.solutions.pose.PoseLandmark
    def pt(i): return (landmarks[i].x, landmarks[i].y)
    def vis(i): return landmarks[i].visibility > vis_thresh

    hip_angles, knee_angles = [], []

    if all(vis(i) for i in [P.LEFT_SHOULDER, P.LEFT_HIP, P.LEFT_KNEE]):
        hip_angles.append(calculate_angle(pt(P.LEFT_SHOULDER), pt(P.LEFT_HIP), pt(P.LEFT_KNEE)))
    if all(vis(i) for i in [P.RIGHT_SHOULDER, P.RIGHT_HIP, P.RIGHT_KNEE]):
        hip_angles.append(calculate_angle(pt(P.RIGHT_SHOULDER), pt(P.RIGHT_HIP), pt(P.RIGHT_KNEE)))

    if all(vis(i) for i in [P.LEFT_HIP, P.LEFT_KNEE, P.LEFT_ANKLE]):
        knee_angles.append(calculate_angle(pt(P.LEFT_HIP), pt(P.LEFT_KNEE), pt(P.LEFT_ANKLE)))
    if all(vis(i) for i in [P.RIGHT_HIP, P.RIGHT_KNEE, P.RIGHT_ANKLE]):
        knee_angles.append(calculate_angle(pt(P.RIGHT_HIP), pt(P.RIGHT_KNEE), pt(P.RIGHT_ANKLE)))

    hip = np.mean([a for a in hip_angles if a is not None]) if hip_angles else None
    knee = np.mean([a for a in knee_angles if a is not None]) if knee_angles else None

    if hip is None or knee is None:
        scores = {"average_score": 0.0}
        return scores

    diff_hip = abs(hip - standard_hip)
    diff_knee = abs(knee - standard_knee)

    hip_score = score_angle(diff_hip, weight=50)
    knee_score = score_angle(diff_knee, weight=50)
    total = round(hip_score + knee_score, 2)

    scores = {"average_score": total}
    return scores



if __name__ == "__main__":
    image_path = r"C:\dataset\bridge_img_filter\pose_3106.jpg"

    standard_hip = 162.94
    standard_knee = 67.88

    with mp.solutions.pose.Pose(static_image_mode=True, model_complexity=1) as pose:
        hip_angle, knee_angle = extract_angles(image_path, pose)

        if hip_angle is not None and knee_angle is not None:
            diff_hip = abs(hip_angle - standard_hip)
            diff_knee = abs(knee_angle - standard_knee)

            hip_score = score_angle(diff_hip, weight=50)
            knee_score = score_angle(diff_knee, weight=50)
            scores = hip_score + knee_score

            print(f"髖關節角度：{hip_angle:.2f}°，差距：{diff_hip:.2f}°，得分：{hip_score:.2f}")
            print(f"膝關節角度：{knee_angle:.2f}°，差距：{diff_knee:.2f}°，得分：{knee_score:.2f}")
            print(f"總分：{scores:.2f} / 100\n")

        else:
            print("無法取得角度資訊")


