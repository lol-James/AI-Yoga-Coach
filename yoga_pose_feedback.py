from threading import Thread, Lock
from PyQt5.QtCore import QThread, QTimer
from Pose_Suggestion import *
import pyttsx3
import time

class YogaPoseFeedback(QThread):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.suggesstion_text_label = self.ui.suggestion_text_label
        
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
            "warrior3": {"Easy": 77, "Hard": 88}
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
            9: "bridge"
        }
        
        self.last_speech_time = 0
        self.speech_interval = 3
        self.tts_lock = Lock()
        
        self.clear_timer = QTimer()
        self.clear_timer.setInterval(3000) # Clear after 3 seconds
        self.clear_timer.timeout.connect(lambda: self.suggesstion_text_label.clear())
        self.clear_timer.start()
        
    def process(self, pose_index, mode, scores):
        pose_name = self.INDEX_TO_KEY.get(pose_index, None)
        if not pose_name or not scores:
            return
        threshold = self.POSE_THRESHOLDS[pose_name][mode]
        feedback_func_map = {
            "bridge": bridge_feedback.get_bridge_feedbackstr,
            "chair": chair_feedback.get_chair_feedbackstr,
            "downward_facing_dog": downward_facing_dog_feedback.get_downward_facing_dog_feedbackstr,
            "locust": locust_feedback.get_locust_feedbackstr,
            "plank": plack_feedback.get_plank_feedbackstr,
            "staff": staff_feedback.get_staff_feedbackstr,
            "triangle": triangle_feedback.get_triangle_feedbackstr,
            "warrior1": warrior1_feedback.get_warrior1_feedbackstr,
            "warrior2": warrior2_feedback.get_warrior2_feedbackstr,
            "warrior3": warrior3_feedback.get_warrior3_feedbackstr    
        }
        feedback_func = feedback_func_map.get(pose_name, None)
        if not feedback_func:
            return
        
        has_error, feedback_str = feedback_func(scores, threshold)
        self.suggesstion_text_label.setText(feedback_str)   
        
        if has_error:
            current_time = time.time()
            if current_time - self.last_speech_time >= self.speech_interval:
                self._speak(feedback_str)
            else:
                pass
        
    def _speak(self, text):
            def tts():
                if not self.tts_lock.acquire(blocking=False):
                    return 
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 200)
                    engine.setProperty('volume', 0.8)
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    print(f"Error in TTS thread: {e}")
                finally:
                    self.last_speech_time = time.time() 
                    self.tts_lock.release() 
            
            Thread(target=tts, daemon=True).start()