import cv2
import mediapipe as mp
import numpy as np

# 閮�蝞���拙�����憭曇��嚗�摨�
def calculate_angle(a, b):
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return None
    unit_a = a / np.linalg.norm(a)
    unit_b = b / np.linalg.norm(b)
    dot_product = np.dot(unit_a, unit_b)
    angle = np.arccos(np.clip(dot_product, -1.0, 1.0))
    return np.degrees(angle)

# ���蝺���扯�������賣��
def score_angle(perfect_angle, actual_angle, weight=33.3, tolerance=5, power=2):
    diff = abs(perfect_angle - actual_angle)
    if diff > 90:
        return 0
    elif diff <= tolerance:
        return weight
    else:
        return weight * (1 - ((diff - tolerance) / (90 - tolerance)) ** power)

# ��桀撐������������
def analyze_image(image_path, perfect_trunk, perfect_pelvis, perfect_shoulder):
    image = cv2.imread(image_path)
    if image is None:
        print("������霈����憭望��")
        return

    h, w, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with mp.solutions.pose.Pose(static_image_mode=True) as pose:
        results = pose.process(image_rgb)

        if not results.pose_landmarks:
            print("��⊥����菜葫憪踹��")
            return

        lm = results.pose_landmarks.landmark
        def pt(index): return np.array([lm[index].x * w, lm[index].y * h])

        # 1. 頠�撟孵����Ｚ��摨�
        mid_hip = (pt(23) + pt(24)) / 2
        mid_shoulder = (pt(11) + pt(12)) / 2
        trunk_vector = mid_shoulder - mid_hip
        vertical_line = np.array([0, -1])
        angle_trunk = calculate_angle(trunk_vector, vertical_line)

        # 2. 撉函��閫�摨佗��撌血�喳之��� ��� �����剁��
        vec_left_leg = pt(23) - pt(25)
        vec_right_leg = pt(24) - pt(26)
        angle_pelvis = calculate_angle(vec_left_leg, vec_right_leg)

        # 3. ��抵��閫�摨佗��撌血�單����� ��� ��抵��嚗�
        vec_left_arm = pt(12) - pt(14)
        vec_right_arm = pt(11) - pt(13)
        angle_shoulder = calculate_angle(vec_left_arm, vec_right_arm)

        if None in [angle_trunk, angle_pelvis, angle_shoulder]:
            print("���閫�摨衣�⊥��閮�蝞�")
            return

        # 閮�蝞�敺����
        trunk_score = score_angle(perfect_trunk, angle_trunk)
        pelvis_score = score_angle(perfect_pelvis, angle_pelvis)
        shoulder_score = score_angle(perfect_shoulder, angle_shoulder)

        scores = trunk_score + pelvis_score + shoulder_score
        
        
        '''
        full_score = 100
        
        print(f"頠�撟孵����Ｚ��摨佗��{angle_trunk:.2f}簞嚗�撌株��嚗�{abs(perfect_trunk - angle_trunk):.2f}簞嚗�敺����嚗�{trunk_score:.2f}")
        print(f"撉函��憭曇��嚗�{angle_pelvis:.2f}簞嚗�撌株��嚗�{abs(perfect_pelvis - angle_pelvis):.2f}簞嚗�敺����嚗�{pelvis_score:.2f}")
        print(f"��抵��憭曇��嚗�{angle_shoulder:.2f}簞嚗�撌株��嚗�{abs(perfect_shoulder - angle_shoulder):.2f}簞嚗�敺����嚗�{shoulder_score:.2f}")
        print(f"蝮賢��嚗�{scores:.2f} / {full_score:.0f}")
        '''
        return scores
'''    
perfect_trunk = 74.74
perfect_pelvis = 69.13
perfect_shoulder = 170.59

# ������頝臬��
image_path = r"C:\dataset\triangle_img_lol\pose_3007.jpg"
analyze_image(image_path, perfect_trunk, perfect_pelvis, perfect_shoulder)
'''