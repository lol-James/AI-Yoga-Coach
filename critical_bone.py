import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal



class Critical_Bone(QThread):
    bone_image= pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        
        
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
        self.body_part ={
            'Hip_Bone': [ 
            # show hip bone, use in the brige/downward_facing_dog/locust/staff/warrior3 pose
            (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP),
            (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_KNEE),
            (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP),
            (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_KNEE)],
            
            'Knee_Bone': [ 
            # show knee bone, use in the brige/downward_facing_dog/locust/staff/warrior1/warrior1 pose
            (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_KNEE),
            (self.mp_pose.PoseLandmark.RIGHT_KNEE, self.mp_pose.PoseLandmark.RIGHT_ANKLE),
            (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_KNEE),
            (self.mp_pose.PoseLandmark.LEFT_KNEE, self.mp_pose.PoseLandmark.LEFT_ANKLE)],
            
            'Arm_Bone': [
            # show arm bone, use in the downward_facing_dog_pose/plank/warrior1/warrior2/warrior3 pose
            (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_ELBOW),
            (self.mp_pose.PoseLandmark.RIGHT_ELBOW, self.mp_pose.PoseLandmark.RIGHT_WRIST),
            (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_ELBOW),
            (self.mp_pose.PoseLandmark.LEFT_ELBOW, self.mp_pose.PoseLandmark.LEFT_WRIST)],
            
            'Armpit_Bone': [
            # show armpit bone, use in the locust/warrior1 pose
            (self.mp_pose.PoseLandmark.RIGHT_ELBOW, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
            (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP),
            (self.mp_pose.PoseLandmark.LEFT_ELBOW, self.mp_pose.PoseLandmark.LEFT_SHOULDER),
            (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP)],
            
            'Head_Bone': [
            # show head bone use in the locust pose
            (self.mp_pose.PoseLandmark.NOSE, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
            (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP),
            (self.mp_pose.PoseLandmark.NOSE, self.mp_pose.PoseLandmark.LEFT_SHOULDER),
            (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP)],
            
            'Body_Bone': [
            # show body bone use in the plank pose
            (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP),
            (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_ANKLE),
            (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP),
            (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_ANKLE)],
            
            'Triangle_bone': [
            # show triangle bone use in the plank pose
            (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_WRIST),
            (self.mp_pose.PoseLandmark.RIGHT_WRIST, self.mp_pose.PoseLandmark.RIGHT_ANKLE),
            (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_WRIST),
            (self.mp_pose.PoseLandmark.LEFT_WRIST, self.mp_pose.PoseLandmark.LEFT_ANKLE)],
            
            'left_leg': [
            # show left leg bone use in the warrior1 pose
            (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_KNEE),
            (self.mp_pose.PoseLandmark.LEFT_KNEE, self.mp_pose.PoseLandmark.LEFT_ANKLE)],
            
            'right_leg': [
            # show right leg bone use in the warrior1 pose
            (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_KNEE),
            (self.mp_pose.PoseLandmark.RIGHT_KNEE, self.mp_pose.PoseLandmark.RIGHT_ANKLE)],
            
            'arm_body_bone': [
            # show arm to body bone use in the warrior2 pose
            (self.mp_pose.PoseLandmark.RIGHT_WRIST, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
            (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP),
            (self.mp_pose.PoseLandmark.LEFT_WRIST, self.mp_pose.PoseLandmark.LEFT_SHOULDER),
            (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP)],
            
            'Upperbody_Bone':[
                (self.mp_pose.PoseLandmark.LEFT_EAR, self.mp_pose.PoseLandmark.LEFT_SHOULDER),
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP),
                (self.mp_pose.PoseLandmark.RIGHT_EAR, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
                (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP)],
            'left_Hip': [
                (self.mp_pose.PoseLandmark.LEFT_KNEE, self.mp_pose.PoseLandmark.LEFT_HIP),
                (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_SHOULDER)],
            'right_Hip': [
                (self.mp_pose.PoseLandmark.RIGHT_KNEE, self.mp_pose.PoseLandmark.RIGHT_HIP),
                (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_SHOULDER)]
        }
        
    def calculate_angle(self,v1, v2):
        
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        if norm_v1 == 0 or norm_v2 == 0: return 0
        cos_angle = np.clip(dot_product / (norm_v1 * norm_v2), -1.0, 1.0)
        angle_rad = np.arccos(cos_angle)
        angle_deg = np.degrees(angle_rad)
        return angle_deg
    
    def draw_bone(self,frame,result,bone):
      
        connection=self.body_part[bone]
        self.mp_drawing.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    connection,
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(0,0,255), thickness=4)
                    )
           
    def draw_torso(self,image, result, mp_pose):
            h, w, _ = image.shape
            landmarks_list = result.pose_landmarks.landmark
            left_shoulder = landmarks_list[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks_list[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_hip = landmarks_list[mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks_list[mp_pose.PoseLandmark.RIGHT_HIP.value]
            
            pt1 = (int((left_shoulder.x + right_shoulder.x) / 2 * w), int((left_shoulder.y + right_shoulder.y) / 2 * h))
            pt2 = (int((left_hip.x + right_hip.x) / 2 * w), int((left_hip.y + right_hip.y) / 2 * h))
            cv2.line(image,pt2,(int((left_hip.x + right_hip.x) / 2 * w),int((left_hip.y + right_hip.y) / 2 * h)-100))
            cv2.line(image, pt1, pt2, 3)
            cv2.circle(image, pt1, 5, -1)
            cv2.circle(image, pt2, 5, -1)
            
    def draw_arm(self,image, result, mp_pose, color):
        self.draw_bone(image,result,'Arm_Bone')
        h, w, _ = image.shape
        landmarks_list = result.pose_landmarks.landmark
        p_ls, p_rs =landmarks_list[mp_pose.PoseLandmark.LEFT_SHOULDER.value], landmarks_list[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        p_le, p_re = landmarks_list[mp_pose.PoseLandmark.LEFT_ELBOW.value],landmarks_list[mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        
        v_left = np.array([p_ls.x - p_le.x, p_ls.y - p_le.y]); v_right = np.array([p_rs.x - p_re.x, p_rs.y - p_re.y])
        center = (int(((p_ls.x + p_rs.x) / 2) * w), int(((p_ls.y + p_rs.y) / 2) * h))
        radius = int(np.linalg.norm(np.array([p_rs.x*w, p_rs.y*h]) - np.array([p_ls.x*w, p_ls.y*h])) / 3)
        if radius < 15: radius = 15
        start_angle = np.degrees(np.arctan2(-v_right[1], v_right[0])); end_angle = np.degrees(np.arctan2(-v_left[1], v_left[0]))
        cv2.ellipse(image, center, (radius, radius), 0, start_angle, end_angle, color, 2)
        
    def draw_leg_angle(self,image, result, mp_pose):

        h, w, _ = image.shape
        
        landmarks_list = result.pose_landmarks.landmark
        left_hip_lm = landmarks_list[mp_pose.PoseLandmark.LEFT_HIP.value]
        left_knee_lm = landmarks_list[mp_pose.PoseLandmark.LEFT_KNEE.value]
        right_hip_lm = landmarks_list[mp_pose.PoseLandmark.RIGHT_HIP.value]
        right_knee_lm = landmarks_list[mp_pose.PoseLandmark.RIGHT_KNEE.value]

       
        p_lh = np.array([left_hip_lm.x, left_hip_lm.y])
        p_lk = np.array([left_knee_lm.x, left_knee_lm.y])
        p_rh = np.array([right_hip_lm.x, right_hip_lm.y])
        p_rk = np.array([right_knee_lm.x, right_knee_lm.y])
        
       
        px_lh = (int(p_lh[0] * w), int(p_lh[1] * h))
        px_rh = (int(p_rh[0] * w), int(p_rh[1] * h))

        self.draw_bone(image,result,'left_leg')
        self.draw_bone(image,result,'right_leg')
        
        v_left = p_lk - p_lh
        v_right = p_rk - p_rh
        
      
        center_px = (int((px_lh[0] + px_rh[0]) / 2), int((px_lh[1] + px_rh[1]) / 2)-20)
        hip_width_px = np.linalg.norm(np.array(px_lh) - np.array(px_rh))
        radius = int(hip_width_px / 3)
        if radius < 20: radius = 20
        
        start_angle_deg = self.calculate_angle(v_left, np.array([1, 0]))
        end_angle_deg = self.calculate_angle(v_right, np.array([1, 0]))
        

        arc_color = (0, 0, 255) # BGR: 青色
        cv2.ellipse(
            image,
            center_px,
            (radius, radius),
            0,
            start_angle_deg,
            end_angle_deg,
            arc_color,
            2
        )
        
    def process(self,pose_id,mode,score,result,frame):
        #id->pose name
        pose_key = self.INDEX_TO_KEY.get(pose_id)
        if mode in["Easy","Hard"]:
            #through pose name and mode get the threshold
            target=self.POSE_THRESHOLDS.get(pose_key, {}).get(mode)
            # if the score lower than target, show critical bone
            try:
                if score['average_score']<target:
                    #get the lowest score part
                    min_key = min(score,  key=lambda k: score[k] if isinstance(score[k], (int, float)) else float('inf'))
                    if min_key in self.body_part:
                        self.draw_bone(frame,result,min_key)
                    elif min_key == 'Trunk':
                        self.draw_torso(frame,result, self.mp_pose)
                    elif min_key == 'Pelvis':
                        self.draw_leg_angle(frame, result, self.mp_pose)
                    elif min_key == 'Shoulder':
                        self.draw_arm(frame, result, self.mp_pose)
                    elif min_key == 'front_leg':
                        leg=score['front'] 
                        if leg=='Left':
                            self.draw_bone(frame,result,'left_leg')
                        elif leg=='Right':
                            self.draw_bone(frame,result,'right_leg')
                    elif min_key == 'back_leg':
                        leg=score['back'] 
                        if leg=='Left':
                            self.draw_bone(frame,result,'left_leg')
                        elif leg=='Right':
                            self.draw_bone(frame,result,'right_leg')  
                    elif min_key == 'Front_Hip_Bone':
                        leg=score['front']
                        if leg=='Left':
                            self.draw_bone(frame, result,'left_Hip')
                        elif leg=='Right':
                            self.draw_bone(frame,result,'right_Hip')
                    elif min_key == 'Hip_Bone_Left':
                        self.draw_bone(frame, result, 'left_Hip')
                    elif min_key == 'Hip_Bone_Right':
                        self.draw_bone(frame, result, 'right_Hip')
                    self.bone_image.emit(frame)
            except Exception as e:
                print("Critical_Bone process error:", e) 
        else:
            return