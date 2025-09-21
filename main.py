import cv2
import os
import pymysql
from Ui_AIYogaCoachInterface import Ui_MainWindow
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap, QIcon
from camera import CameraThread
from yoga_pose_detector import YogaPoseDetector
from musicPlayer import MusicPlayer
from gesture import GestureAnalyzer, GestureInterpreter
from notification import NotificationLabel
from countdownTimer import Timer
from record_logger import RecordLogger
from user_info import User_Info
from account import Account
from yoga_pose_calculate import evaluate_and_display_pose
from postdialog import PostDialog
from pose_thresholds import is_pose_score_valid

class AIYogaCoachApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # gui initialization
        self.window = Ui_MainWindow()
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowIcon(QIcon("icons/yoga-logo.png"))
        self.maximize_btn.setCheckable(True)
        self.maximize_btn.clicked.connect(lambda: self.showNormal() if self.isFullScreen() else self.showFullScreen())
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.close_btn.clicked.connect(self.close)
        self.old_pos = self.pos()
        self.mouse_pressed = False
        self.full_menu_frame.setHidden(True)
        self.full_home_btn.setCheckable(True)
        button_index_map = {
            self.home_btn: 0, self.full_home_btn: 0, self.music_btn: 1, self.full_music_btn: 1,
            self.progress_btn: 2, self.full_progress_btn: 2, self.share_btn: 3, self.full_share_btn: 3,  
            self.account_btn: 4, self.full_account_btn: 4, self.info_btn: 5, self.full_info_btn: 5
        }
        for btn, index in button_index_map.items():
            btn.toggled.connect(lambda checked, i=index, b=btn: self.navigate_with_auth(i, checked, b))
        self.image_index = 0
        self.demo_list.setEnabled(False)
        self.load_demo_image()

        # sql variables
        self.db=self.connect_db()
        
        # camera and yoga detector initializations
        self.camera_thread = CameraThread()
        self.camera_thread.new_frame.connect(self.update_current_frame)
        self.detector = YogaPoseDetector()
        self.detector.result_image_signal.connect(self.update_GUI_frame)
        self.camera_btn.toggled.connect(self.on_camera_btn_toggled)

        # share page
        self.addShareicon.setCheckable(True)
        self.share_comment_btn.setCheckable(True)
        self.share_cancel_btn.setCheckable(True)
        self.widget_6.hide()
        self.share_comment_frame.hide()
        self.addShareicon.clicked.connect(self.show_share_page_widget)
        self.share_comment_btn.clicked.connect(self.toggle_share_comment_widget)
        self.share_cancel_btn.clicked.connect(self.hide_share_page_widget)

        # account
        self.account = Account(self, self.on_camera_btn_toggled)
        
        # user info
        self.user_info= User_Info(self, self.account.user_id)
        print("start")

        # Music Player
        self.music_player = MusicPlayer(self)

        #Share Page Funtions
        self.post_dialog = PostDialog(self, self.account.user_id, self.db)
        self.post_dialog.load_posts()

        # mediapipe gesture analyzer initialization
        self.gesture_analyzer = GestureAnalyzer()
        self.gesture_interpreter = GestureInterpreter(self)
        self.gesture_analyzer.result_str_signal.connect(self.gesture_interpreter.interpret)
        self.gesture_analyzer.touch_note_signal.connect(self.toggle_touch_note)
        self.show()

        # timer
        self.countdown_timer = Timer(self)

        # record logger
        self.logger = RecordLogger(ui=self)
        self.account.user_id_signal.connect(self.user_info.on_signal_received)
        self.account.user_id_signal.connect(self.music_player.update_user_id)
        self.account.user_id_signal.connect(self.post_dialog.update_user_id)
        self.user_info.del_user_account_signal.connect(self.account.logout)

        # calculate score and display
        self.detector.result_pose_signal.connect(self.cache_pose_index)
        self.pose_score_timer = QTimer()
        self.pose_score_timer.timeout.connect(self.perform_pose_scoring)
        self.pose_score_timer.start(500)  

        self.pose_name_map = {
            "Downward Facing Dog": "Downward-Facing_Dog",
            "Warrior 1": "Warrior_I",
            "Warrior 2": "Warrior_II",
            "Warrior 3": "Warrior_III",
            "Plank Pose": "Plank_Pose",
            "Staff Pose": "Staff_Pose",
            "Chair Pose": "Chair_Pose",
            "Locust Pose": "Locust_Pose",
            "Triangle Pose": "Triangle_Pose",
            "Bridge Pose": "Bridge_Pose"
        }
    
    def navigate_with_auth(self, index, checked, button):
        if not checked:
            return  

        if index not in [1, 5] and not self.account.login_flag:
            NotificationLabel(self, "Please login first to unlock the features.", success=False)
            button.setChecked(False)
            return
        
        if self.stackedWidget.currentIndex() != 0:
            self.on_camera_btn_toggled()  
        
        self.stackedWidget.setCurrentIndex(index)


    def mousePressEvent(self, event):
        if self.title_frame.underMouse():  
            self.old_pos = event.globalPos()
            self.mouse_pressed = True

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            
    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False

    def update_current_frame(self, frame):
        self.detector.frame = frame
        self.gesture_analyzer.frame = frame
        
    def update_GUI_frame(self, processed_frame):
        if not processed_frame is None:
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_label.setPixmap(pixmap)
    
    def on_camera_btn_toggled(self):
        if self.account.login_flag:
                if self.stackedWidget.currentIndex() == 0:
                    if self.camera_btn.isChecked():
                        self.camera_thread.start()
                        self.detector.start()
                        self.gesture_analyzer.start()
                        self.countdown_timer.camera_is_running = True
                        NotificationLabel(self, "Camera opened", success=True)

                    else:
                        self.camera_thread.stop()
                        self.detector.stop()
                        self.gesture_analyzer.stop()
                        self.countdown_timer.camera_is_running = False
                        if self.countdown_timer.timer_is_running:
                            self.countdown_timer._stop_timer()
                        QTimer.singleShot(100, lambda: self.clear_camera_label())
                        NotificationLabel(self, "Camera closed", success=True)

                elif self.camera_btn.isChecked():
                    self.camera_btn.setChecked(False)
                    self.camera_thread.stop()
                    self.detector.stop()
                    self.gesture_analyzer.stop()
                    self.countdown_timer.camera_is_running = False
                    self.countdown_timer._stop_timer()
                    QTimer.singleShot(100, lambda: self.clear_camera_label())
                    NotificationLabel(self, "Camera closed", success=False)

        else:
            self.camera_btn.setChecked(False)
            NotificationLabel(self, "Please login first to unlock all features.", success=False)
        
    def clear_camera_label(self):
        self.camera_label.setPixmap(QPixmap())
        self.camera_label.setText('Lens screen not found')
            
    def show_share_page_widget(self):
            if self.addShareicon.isChecked():
                    self.widget_6.show()
    
    def toggle_share_comment_widget(self):
        if self.share_comment_frame.isVisible():
            self.share_comment_frame.hide()
        else:
            self.share_comment_frame.show()
    
    def hide_share_page_widget(self):
            if self.share_cancel_btn.isChecked():
                    self.widget_6.hide()
    
    def load_demo_image(self):
        self.image_dir = r"YOLO\demo_images"
        self.image_list = [file for file in os.listdir(self.image_dir) if file.endswith(('.png', '.jpg', '.jpeg'))]
        self.image_index = 0

        if not self.image_list:
            QMessageBox.warning(self, 'Error', 'No images found in demo_images folder.')
            return

        for image_name in self.image_list:
            self.demo_list.addItem(os.path.splitext(image_name)[0])
        
        self.demo_list.scrollToBottom()
        self.display_image(self.image_list[self.image_index])
    
    def reset_to_first_image(self):
        if not hasattr(self, 'image_list') or not self.image_list:
            QMessageBox.warning(self, 'Error', 'No images to display. Please load images first.')
            return

        self.image_index = 0  
        self.display_image(self.image_list[self.image_index])

    def display_image(self, image_name):
        image_path = os.path.join(self.image_dir, image_name)
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            QMessageBox.warning(self, 'Error', f'Unable to load image: {image_path}')
            return

        self.demo_label.setPixmap(pixmap)
        self.demo_list.setCurrentRow(self.image_index)

    def next_pose(self, skip_flag):
        print('Next Pose')
        if not hasattr(self, 'image_list') or not self.image_list:
            QMessageBox.warning(self, 'Error', 'No images to display. Please load images first.')
            return
        
        if self.countdown_timer.timer_is_running:
            self.countdown_timer.skip(skip_flag)

        self.image_index = (self.image_index + 1) % len(self.image_list)
        self.display_image(self.image_list[self.image_index])
        
    def previous_pose(self, skip_flag):
        print('Prvious Pose')
        if not hasattr(self, 'image_list') or not self.image_list:
            QMessageBox.warning(self, 'Error', 'No images to display. Please load images first.')
            return
        
        if self.countdown_timer.timer_is_running:
            self.countdown_timer.skip(skip_flag)

        self.image_index = (self.image_index - 1) % len(self.image_list)
        self.display_image(self.image_list[self.image_index])
    
    def toggle_touch_note(self, str):
        self.gesture_analyzer.enabled = not self.gesture_analyzer.enabled
        if self.gesture_analyzer.enabled:
            NotificationLabel(self, f"Gesture control enabled", success=True)
        else:    
            NotificationLabel(self, f"Gesture control disabled", success=False)

    #connect to database
    def connect_db(self):
        try:
            db = pymysql.connect(
                host='127.0.0.1',
                user='root',
                password='root123456',
                database='yoga_coach_database',
                port=3306,
                cursorclass=pymysql.cursors.DictCursor
            )
            print("pymysql connected successfully")
            return db
        except Exception as e:
            print("pymysql connection error: ", e)

    def cache_pose_index(self, pose_index):
        self.current_pose_index = pose_index

    def perform_pose_scoring(self):
        if not hasattr(self, 'current_pose_index') or not getattr(self.detector, "yolo_has_person", False) \
            or not self.countdown_timer.camera_is_running or self.state_reg_label.text() != "Exercise" \
            or self.detector.frame is None:
            self.countdown_timer.on_pose_detected(False)
            return
        
        current_demo_item = self.demo_list.currentItem()
        selected_display_name = current_demo_item.text().strip()
        selected_pose_name = self.pose_name_map.get(selected_display_name)
        detected_pose_name = self.detector.pose_names[self.current_pose_index]

        if current_demo_item is None or selected_pose_name is None or detected_pose_name != selected_pose_name:
            self.countdown_timer.on_pose_detected(False)
            return
        
        isUpdated = False

        if detected_pose_name == selected_pose_name:
            avg = evaluate_and_display_pose(
                self.detector.frame,
                self.current_pose_index,
                self.pose_reg_label
            )

            if avg and avg > 0:
                # ✅ 呼叫獨立的判斷模組
                mode = self.countdown_timer.mode
                isUpdated = is_pose_score_valid(self.current_pose_index, avg, mode)

        self.countdown_timer.on_pose_detected(isUpdated)

