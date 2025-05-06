import cv2
from PyQt5.QtCore import QThread, pyqtSignal
import time
import math
import mediapipe as mp
from notification import NotificationLabel

class GestureAnalyzer(QThread):
    processed_image_signal = pyqtSignal(object)
    result_str_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.frame = None
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.last_gesture = None
        self.last_time = 0
        self.is_running = False
        
    def vector_2d_angle(self, v1, v2):
        v1_x = v1[0]
        v1_y = v1[1]
        v2_x = v2[0]
        v2_y = v2[1]
        try:
            angle_ = math.degrees(math.acos((v1_x*v2_x + v1_y*v2_y) / (((v1_x**2 + v1_y**2)**0.5) * ((v2_x**2 + v2_y**2)**0.5))))
        except:
            angle_ = 180
        return angle_

    def hand_angle(self, hand_):
        angle_list = []
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[2][0])), (int(hand_[0][1])- int(hand_[2][1]))),
            ((int(hand_[3][0])- int(hand_[4][0])), (int(hand_[3][1])- int(hand_[4][1])))
        )
        angle_list.append(angle_)
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[6][0])), (int(hand_[0][1])- int(hand_[6][1]))),
            ((int(hand_[7][0])- int(hand_[8][0])), (int(hand_[7][1])- int(hand_[8][1])))
        )
        angle_list.append(angle_)
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[10][0])), (int(hand_[0][1])- int(hand_[10][1]))),
            ((int(hand_[11][0])- int(hand_[12][0])), (int(hand_[11][1])- int(hand_[12][1])))
        )
        angle_list.append(angle_)
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[14][0])), (int(hand_[0][1])- int(hand_[14][1]))),
            ((int(hand_[15][0])- int(hand_[16][0])), (int(hand_[15][1])- int(hand_[16][1])))
        )
        angle_list.append(angle_)
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[18][0])), (int(hand_[0][1])- int(hand_[18][1]))),
            ((int(hand_[19][0])- int(hand_[20][0])), (int(hand_[19][1])- int(hand_[20][1])))
        )
        angle_list.append(angle_)
        return angle_list

    def get_thumb_direction(self, finger_points):
        thumb_start = finger_points[0]
        thumb_end = finger_points[4]

        thumb_vector = (thumb_end[0] - thumb_start[0], thumb_end[1] - thumb_start[1])

        # Determine the direction based on the vector of the thumb
        if abs(thumb_vector[0]) > abs(thumb_vector[1]):  # Horizontal direction larger
            if thumb_vector[0] > 0:
                return "Right"
            else:
                return "Left"
        else: 
            if thumb_vector[1] > 0:
                return "Down"
            else:
                return "Up"
                
    def hand_pos(self, finger_points,finger_angle):
        f1 = finger_angle[0]   # 大拇指
        f2 = finger_angle[1]   # 食指
        f3 = finger_angle[2]   # 中指
        f4 = finger_angle[3]   # 無名指
        f5 = finger_angle[4]   # 小拇指

        # <50: straight, >=50: curled
        if f1 < 50 and f2 >= 50 and f3 >= 50 and f4 >= 50 and f5 >= 50:
            return self.get_thumb_direction(finger_points)
        elif f1 < 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 < 50:
            return 'Rock!'
        elif f1 >= 50 and f2 >= 50 and f3 >= 50 and f4 >= 50 and f5 >= 50:
            return '0'
        elif f1 >= 50 and f2 >= 50 and f3 >= 50 and f4 >= 50 and f5 < 50:
            return 'Pinky'
        elif f1 >= 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 >= 50:
            return '1'
        elif f1 >= 50 and f2 < 50 and f3 < 50 and f4 >= 50 and f5 >= 50:
            return '2'
        elif f1 >= 50 and f2 >= 50 and f3 < 50 and f4 < 50 and f5 < 50:
            return 'ok'
        elif f1 >= 50 and f2 < 50 and f3 < 50 and f4 < 50 and f5 > 50:
            return '3'
        elif f1 >= 50 and f2 < 50 and f3 < 50 and f4 < 50 and f5 < 50:
            return '4'
        elif f1 < 50 and f2 < 50 and f3 < 50 and f4 < 50 and f5 < 50:
            return '5'
        elif f1 < 50 and f2 >= 50 and f3 >= 50 and f4 >= 50 and f5 < 50:
            return '6'
        elif f1 < 50 and f2 < 50 and f3 >= 50 and f4 >= 50 and f5 >= 50:
            return '7'
        elif f1 < 50 and f2 < 50 and f3 < 50 and f4 >= 50 and f5 >= 50:
            return '8'
        elif f1 < 50 and f2 < 50 and f3 < 50 and f4 < 50 and f5 >= 50:
            return '9'
        else:
            return ''
    
    def run(self):
        self.is_running = True
        self.frame = None
        with self.mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.5) as hands:

            while self.is_running:
                if self.frame is None:
                    continue
                global img
                img = cv2.resize(self.frame, (500, 300)) 
                global h, w
                h, w, _ = img.shape
                img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = hands.process(img2)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        self.mp_drawing.draw_landmarks(
                            img,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.mp_drawing_styles.get_default_hand_landmarks_style(),
                            self.mp_drawing_styles.get_default_hand_connections_style())

                        finger_points = []
                        for i in hand_landmarks.landmark:
                            x = int(i.x * w)
                            y = int(i.y * h)
                            finger_points.append((x, y))

                        if finger_points:
                            finger_angle = self.hand_angle(finger_points)
                            text = self.hand_pos(finger_points, finger_angle)
                            if text == self.last_gesture:
                                if time.time() - self.last_time > 2:
                                    self.result_str_signal.emit(text)
                                    self.last_time = time.time()
                            else:
                                self.last_gesture = text
                                self.last_time = time.time()
                                
                self.processed_image_signal.emit(img)

    def stop(self):
        self.is_running = False
        self.wait()

class GestureInterpreter:
    def __init__(self, parent):
        self.parent = parent  

        self.gesture_actions = {
            '0': (self.parent.music_player.toggle_mute, "Gesture 0: Toggle Mute"),
            'Up': (self.parent.next_pose, "Gesture Up: Next Pose"),
            'Down': (self.parent.previous_pose, "Gesture Down: Previous Pose"),
            'Left': (self.parent.songlist_btn.click, "Gesture Left: Open Song List"),
            'Right': (self.parent.favorites_btn.click, "Gesture Right: Open Favorites"),
            '1': (self.parent.play_btn.click, "Gesture 1: Play Song"),
            '2': (self.parent.pause_btn.click, "Gesture 2: Pause Song"),
            '3': (self.parent.stop_btn.click, "Gesture 3: Stop Song"),
            '4': (self.parent.previous_btn.click, "Gesture 4: Previous Song"),
            '5': (self.parent.next_btn.click, "Gesture 5: Next Song"),
            '6': (self.parent.shuffle_songs_btn.click, "Gesture 6: Shuffle Songs"),
            '7': (self.parent.loop_one_btn.click, "Gesture 7: Loop One Song"),
            '8': (self.parent.add_to_fav_btn.click, "Gesture 8: Add to Favorites")
        }

    def interpret(self, gesture_str):
        if gesture_str in self.gesture_actions:
            action, message = self.gesture_actions[gesture_str]
            action()  
            NotificationLabel(self.parent, message, success=True)  
        else:
            NotificationLabel(self.parent, f"Unrecognized Gesture: {gesture_str}", success=False)
