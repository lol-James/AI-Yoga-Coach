import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

class Critical_Bone(QThread):
    # Signal to emit the frame with drawn bones
    bone_image = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        # Initialize MediaPipe drawing and pose modules
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        
        # Thresholds for each pose type at different difficulties
        self.POSE_THRESHOLDS = {
            "bridge": {"Easy": 88, "Hard": 95},
            "chair": {"Easy": 78, "Hard": 90},
            "downward_facing_dog": {"Easy": 83, "Hard": 94},
            "locust": {"Easy": 80, "Hard": 90},
            "plank": {"Easy": 85, "Hard": 94},
            "staff": {"Easy": 86, "Hard": 94},
            "triangle": {"Easy": 82, "Hard": 91},
            "warrior1": {"Easy": 72, "Hard": 87},
            "warrior2": {"Easy": 83, "Hard": 91},
            "warrior3": {"Easy": 77, "Hard": 88},
        }

        # Map index to pose names
        self.INDEX_TO_KEY = {
            0: "downward_facing_dog",
            1: "warrior1",
            2: "warrior2",
            3: "warrior3",
            4: "plank",
            5: "staff",
            6: "chair",      
            7: "locust",
            8: "triangle",
            9: "bridge",
        }

        # Define critical bones for drawing in each pose
        self.body_part = {
            'Hip_Bone': [  # Hip connections
                (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP),
                (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_KNEE),
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP),
                (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_KNEE)],
            
            'Knee_Bone': [  # Knee connections
                (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_KNEE),
                (self.mp_pose.PoseLandmark.RIGHT_KNEE, self.mp_pose.PoseLandmark.RIGHT_ANKLE),
                (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_KNEE),
                (self.mp_pose.PoseLandmark.LEFT_KNEE, self.mp_pose.PoseLandmark.LEFT_ANKLE)],
            
            'Arm_Bone': [  # Arm connections
                (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_ELBOW),
                (self.mp_pose.PoseLandmark.RIGHT_ELBOW, self.mp_pose.PoseLandmark.RIGHT_WRIST),
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_ELBOW),
                (self.mp_pose.PoseLandmark.LEFT_ELBOW, self.mp_pose.PoseLandmark.LEFT_WRIST)],
            
            'Armpit_Bone': [  # Armpit connections
                (self.mp_pose.PoseLandmark.RIGHT_ELBOW, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
                (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP),
                (self.mp_pose.PoseLandmark.LEFT_ELBOW, self.mp_pose.PoseLandmark.LEFT_SHOULDER),
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP)],
            
            'Head_Bone': [  # Head connections
                (self.mp_pose.PoseLandmark.NOSE, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
                (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP),
                (self.mp_pose.PoseLandmark.NOSE, self.mp_pose.PoseLandmark.LEFT_SHOULDER),
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP)],
            
            'Body_Bone': [  # Torso connections for plank pose
                (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP),
                (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_ANKLE),
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP),
                (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_ANKLE)],
            
            'Triangle_bone': [  # Triangle pose bones
                (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_WRIST),
                (self.mp_pose.PoseLandmark.RIGHT_WRIST, self.mp_pose.PoseLandmark.RIGHT_ANKLE),
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_WRIST),
                (self.mp_pose.PoseLandmark.LEFT_WRIST, self.mp_pose.PoseLandmark.LEFT_ANKLE)],
            
            'left_leg': [  # Left leg bones for warrior1
                (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_KNEE),
                (self.mp_pose.PoseLandmark.LEFT_KNEE, self.mp_pose.PoseLandmark.LEFT_ANKLE)],
            
            'right_leg': [  # Right leg bones for warrior1
                (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_KNEE),
                (self.mp_pose.PoseLandmark.RIGHT_KNEE, self.mp_pose.PoseLandmark.RIGHT_ANKLE)],
            
            'arm_body_bone': [  # Arm to body bones for warrior2
                (self.mp_pose.PoseLandmark.RIGHT_WRIST, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
                (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP),
                (self.mp_pose.PoseLandmark.LEFT_WRIST, self.mp_pose.PoseLandmark.LEFT_SHOULDER),
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP)],
            
            'Upperbody_Bone': [  # Upper body connections
                (self.mp_pose.PoseLandmark.LEFT_EAR, self.mp_pose.PoseLandmark.LEFT_SHOULDER),
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP),
                (self.mp_pose.PoseLandmark.RIGHT_EAR, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
                (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP)],
            
            'left_Hip': [  # Left hip bones
                (self.mp_pose.PoseLandmark.LEFT_KNEE, self.mp_pose.PoseLandmark.LEFT_HIP),
                (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_SHOULDER)],
            
            'right_Hip': [  # Right hip bones
                (self.mp_pose.PoseLandmark.RIGHT_KNEE, self.mp_pose.PoseLandmark.RIGHT_HIP),
                (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_SHOULDER)]
        }

    # -----------------------------
    # Calculate angle between two vectors
    # -----------------------------
    def calculate_angle(self, v1, v2):
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        if norm_v1 == 0 or norm_v2 == 0:
            return 0
        cos_angle = np.clip(dot_product / (norm_v1 * norm_v2), -1.0, 1.0)
        angle_rad = np.arccos(cos_angle)
        return np.degrees(angle_rad)

    # -----------------------------
    # Draw a specific bone on the frame
    # -----------------------------
    def draw_bone(self, frame, result, bone):
        connection = self.body_part[bone]
        self.mp_drawing.draw_landmarks(
            frame,
            result.pose_landmarks,
            connection,
            connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0,0,255), thickness=4)
        )

    # -----------------------------
    # Draw torso as a line between shoulders and hips
    # -----------------------------
    def draw_torso(self, image, result, mp_pose):
        h, w, _ = image.shape
        landmarks = result.pose_landmarks.landmark
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

        pt1 = (int((left_shoulder.x + right_shoulder.x)/2 * w), int((left_shoulder.y + right_shoulder.y)/2 * h))
        pt2 = (int((left_hip.x + right_hip.x)/2 * w), int((left_hip.y + right_hip.y)/2 * h))
        cv2.line(image, pt1, pt2, 3)
        cv2.circle(image, pt1, 5, -1)
        cv2.circle(image, pt2, 5, -1)

    # -----------------------------
    # Draw arm with an arc representing angle
    # -----------------------------
    def draw_arm(self, image, result, mp_pose, color):
        self.draw_bone(image, result, 'Arm_Bone')
        h, w, _ = image.shape
        landmarks = result.pose_landmarks.landmark
        p_ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        p_rs = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        p_le = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
        p_re = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value]

        v_left = np.array([p_ls.x - p_le.x, p_ls.y - p_le.y])
        v_right = np.array([p_rs.x - p_re.x, p_rs.y - p_re.y])
        center = (int(((p_ls.x + p_rs.x)/2)*w), int(((p_ls.y + p_rs.y)/2)*h))
        radius = int(np.linalg.norm(np.array([p_rs.x*w, p_rs.y*h]) - np.array([p_ls.x*w, p_ls.y*h])) / 3)
        radius = max(radius, 15)
        start_angle = np.degrees(np.arctan2(-v_right[1], v_right[0]))
        end_angle = np.degrees(np.arctan2(-v_left[1], v_left[0]))
        cv2.ellipse(image, center, (radius, radius), 0, start_angle, end_angle, color, 2)

    # -----------------------------
    # Draw leg angle arc
    # -----------------------------
    def draw_leg_angle(self, image, result, mp_pose):
        h, w, _ = image.shape
        landmarks = result.pose_landmarks.landmark
        left_hip, left_knee = np.array([landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]), np.array([landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y])
        right_hip, right_knee = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]), np.array([landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y])
        
        self.draw_bone(image, result, 'left_leg')
        self.draw_bone(image, result, 'right_leg')

        center_px = (int((left_hip[0]*w + right_hip[0]*w)/2), int((left_hip[1]*h + right_hip[1]*h)/2)-20)
        hip_width_px = np.linalg.norm(np.array([left_hip[0]*w, left_hip[1]*h]) - np.array([right_hip[0]*w, right_hip[1]*h]))
        radius = max(int(hip_width_px / 3), 20)

        start_angle_deg = self.calculate_angle(left_knee - left_hip, np.array([1,0]))
        end_angle_deg = self.calculate_angle(right_knee - right_hip, np.array([1,0]))

        cv2.ellipse(image, center_px, (radius, radius), 0, start_angle_deg, end_angle_deg, (0,0,255), 2)

    # -----------------------------
    # Process frame: highlight critical bone with lowest score
    # -----------------------------
    def process(self, score, result, frame):
        try:
            min_key = min(score, key=lambda k: score[k] if isinstance(score[k], (int,float)) else float('inf'))
            if min_key in self.body_part:
                self.draw_bone(frame, result, min_key)
            elif min_key == 'Trunk':
                self.draw_torso(frame, result, self.mp_pose)
            elif min_key == 'Pelvis':
                self.draw_leg_angle(frame, result, self.mp_pose)
            elif min_key == 'Shoulder':
                self.draw_arm(frame, result, self.mp_pose)
            elif min_key == 'front_leg':
                leg = score['front']
                if leg == 'Left': self.draw_bone(frame, result, 'left_leg')
                elif leg == 'Right': self.draw_bone(frame, result, 'right_leg')
            elif min_key == 'back_leg':
                leg = score['back']
                if leg == 'Left': self.draw_bone(frame, result, 'left_leg')
                elif leg == 'Right': self.draw_bone(frame, result, 'right_leg')
            elif min_key == 'Front_Hip_Bone':
                leg = score['front']
                if leg == 'Left': self.draw_bone(frame, result, 'left_Hip')
                elif leg == 'Right': self.draw_bone(frame, result, 'right_Hip')
            elif min_key == 'Hip_Bone_Left':
                self.draw_bone(frame, result, 'left_Hip')
            elif min_key == 'Hip_Bone_Right':
                self.draw_bone(frame, result, 'right_Hip')
            return frame
        except Exception as e:
            print("Critical_Bone process error:", e)
