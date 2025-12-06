import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import cv2
import os
import pymysql
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import generate_chart
from datetime import datetime, timedelta, time as dtime
from Ui_AIYogaCoachInterface import Ui_MainWindow
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap, QIcon, QFont
from camera import CameraThread
from yoga_pose_detector import YogaPoseDetector
from musicPlayer import MusicPlayer
from gesture import GestureAnalyzer, GestureInterpreter
from notification import NotificationLabel
from countdownTimer import Timer
from record_logger import RecordLogger
from user_info import User_Info
from account import Account
from yoga_pose_calculate import PoseCalculate
from postdialog import PostDialog
from pose_thresholds import is_pose_score_valid
from pose_thresholds import display_standard_score
from critical_bone import Critical_Bone
from yoga_pose_feedback import YogaPoseFeedback
from keep_db_alive_timer import start_keep_db_alive_timer
import numpy as np

class AIYogaCoachApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        # -----------------------------
        # GUI WINDOW INITIALIZATION
        # -----------------------------
        self.window = Ui_MainWindow()
        self.setupUi(self)

        # Make the window frameless + transparent background
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Application icon
        self.setWindowIcon(QIcon("icons/yoga-logo.png"))

        # Window control buttons formatting
        self.maximize_btn.setCheckable(True)
        self.maximize_btn.clicked.connect(
            lambda: self.showNormal() if self.isFullScreen() else self.showFullScreen()
        )
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.close_btn.clicked.connect(self.close)

        # Variables for moving the frameless window
        self.old_pos = self.pos()
        self.mouse_pressed = False

        # Set full side menu initially hidden
        self.full_menu_frame.setHidden(True)
        self.full_home_btn.setCheckable(True)

        # -----------------------------
        # PAGE NAVIGATION SETUP
        # Each button maps to a stackedWidget index
        # -----------------------------
        button_index_map = {
            self.home_btn: 0, self.full_home_btn: 0,
            self.music_btn: 1, self.full_music_btn: 1,
            self.progress_btn: 2, self.full_progress_btn: 2,
            self.share_btn: 3, self.full_share_btn: 3,
            self.account_btn: 4, self.full_account_btn: 4,
            self.info_btn: 5, self.full_info_btn: 5
        }

        # When a button is toggled → navigate (with login check)
        for btn, index in button_index_map.items():
            btn.toggled.connect(lambda checked, i=index, b=btn: self.navigate_with_auth(i, checked, b))

        # -----------------------------
        # HOME PAGE DEMO IMAGES
        # -----------------------------
        self.image_index = 0
        self.demo_list.setEnabled(False)
        self.load_demo_image()

        # -----------------------------
        # SQL / DATABASE CONNECTION
        # -----------------------------
        self.db = self.connect_db()
        self.keep_db_alive_timer = start_keep_db_alive_timer(self.db)

        # -----------------------------
        # CAMERA THREAD + YOLO DETECTOR
        # -----------------------------
        self.camera_thread = CameraThread()
        self.camera_thread.new_frame.connect(self.update_current_frame)

        self.detector = YogaPoseDetector()
        self.detector.result_image_signal.connect(self.update_GUI_frame)

        # Camera toggle button
        self.camera_btn.toggled.connect(self.on_camera_btn_toggled)

        # -----------------------------
        # SHARE PAGE INITIALIZATION
        # -----------------------------
        self.addShareicon.setCheckable(False)
        self.share_comment_btn.setCheckable(True)
        self.share_cancel_btn.setCheckable(False)

        self.frame_12.hide()
        self.share_comment_frame.hide()

        self.addShareicon.clicked.connect(self.show_share_page_widget)
        self.share_comment_btn.clicked.connect(self.toggle_share_comment_widget)
        self.share_cancel_btn.clicked.connect(self.hide_share_page_widget)

        # -----------------------------
        # ACCOUNT SYSTEM
        # -----------------------------
        self.account = Account(self, self.on_camera_btn_toggled)

        # USER INFO PAGE
        self.user_info = User_Info(self, self.account.user_id)
        print("start")

        # -----------------------------
        # MUSIC PLAYER
        # -----------------------------
        self.music_player = MusicPlayer(self)

        # -----------------------------
        # SHARE PAGE: load existing posts
        # -----------------------------
        self.post_dialog = PostDialog(self, self.account.user_id, self.db)
        self.post_dialog.load_posts()

        # -----------------------------
        # HAND GESTURE ANALYZER (MediaPipe)
        # -----------------------------
        self.gesture_analyzer = GestureAnalyzer()
        self.gesture_interpreter = GestureInterpreter(self)

        # Connect gesture signals
        self.gesture_analyzer.result_str_signal.connect(self.gesture_interpreter.interpret)
        self.gesture_analyzer.touch_note_signal.connect(self.toggle_touch_note)

        self.show()

        # -----------------------------
        # COUNTDOWN TIMER
        # -----------------------------
        self.countdown_timer = Timer(self)

        # -----------------------------
        # RECORD LOGGER
        # Handles session logging, posture data, statistics
        # -----------------------------
        self.logger = RecordLogger(ui=self, db=self.db)

        # Update logger user id when account emits id
        self.account.user_id_signal.connect(self.logger.set_user_id)
        self.account.user_id_signal.connect(lambda uid: self.on_reset_clicked() if uid else None)

        # Start session upon login, end session on logout
        self.account.user_id_signal.connect(
            lambda uid: self.logger.start_session(self.countdown_timer.mode)
            if uid else self.logger.end_session()
        )

        # Other update operations triggered by login/logout
        self.account.user_id_signal.connect(
            lambda uid: self.update_progress_page_statistics(self.countdown_timer.mode)
        )
        self.account.user_id_signal.connect(self.user_info.on_signal_received)
        self.account.user_id_signal.connect(self.music_player.update_user_id)
        self.account.user_id_signal.connect(self.post_dialog.update_user_id)

        # Delete user action
        self.user_info.del_user_account_signal.connect(self.account.logout)

        # -----------------------------
        # INIT STATISTICS SNAPSHOT
        # Used for computing delta for each pose category
        # -----------------------------
        self._tree_counts_snapshot = []
        for i in range(len(self.logger.pose_names)):
            item = self.countdown_timer.statistics_treewidget.topLevelItem(i)
            try:
                v = int(item.text(1)) if item and item.text(1).isdigit() else 0
            except Exception:
                v = 0
            self._tree_counts_snapshot.append(v)

        # When tree item changes → compute statistics difference
        self.countdown_timer.statistics_treewidget.itemChanged.connect(self.on_tree_item_changed)

        # -----------------------------
        # MODE: Practice / Easy / Hard
        # -----------------------------
        self.label_16.setText("Practice")

        self.practice_btn.clicked.connect(lambda: self.on_mode_changed("Practice"))
        self.easy_btn.clicked.connect(lambda: self.on_mode_changed("Easy"))
        self.hard_btn.clicked.connect(lambda: self.on_mode_changed("Hard"))

        self.difficulties = ["Practice", "Easy", "Hard"]
        self.pushButton_7.clicked.connect(self.on_prev_mode)
        self.pushButton_8.clicked.connect(self.on_next_mode)

        # Lock mode buttons while timer is running
        self.countdown_timer.timer_started_signal.connect(lambda: self.toggle_mode_buttons(False))
        self.countdown_timer.timer_stopped_signal.connect(lambda: self.toggle_mode_buttons(True))

        # -----------------------------
        # POSE SCORING SYSTEM
        # Mediapipe angle scoring + incorrect bone highlighting
        # -----------------------------
        self.pose_calculator = PoseCalculate()
        self.critical_bone = Critical_Bone()
        self.yoga_pose_feedback = YogaPoseFeedback(self)

        # Receive scoring result from pose_calculator
        self.pose_calculator.score_result.connect(
            lambda score, result: self.set_draw_bone_variable(score, result)
        )

        # Display textual feedback
        self.pose_calculator.score_result.connect(
            lambda score, result: self.yoga_pose_feedback.process(
                self.current_pose_index, self.countdown_timer.mode, score
            )
        )

        # YOLO pose index cache
        self.detector.result_pose_signal.connect(self.cache_pose_index)

        # Timer for pose scoring every second
        self.countdown_timer.pose_scoring_request.connect(self.perform_pose_scoring)

        self.wakeup_timer_timer = QTimer(self)
        self.wakeup_timer_timer.timeout.connect(self.wakeup_timer)
        self.wakeup_timer_timer.start(100)

        # Mapping display names → YOLO pose names
        self.pose_name_map = {
            "Bridge Pose": "Bridge_Pose",
            "Chair Pose": "Chair_Pose",
            "Downward Facing Dog": "Downward-Facing_Dog",
            "Locust Pose": "Locust_Pose",
            "Plank Pose": "Plank_Pose",
            "Staff Pose": "Staff_Pose",
            "Triangle Pose": "Triangle_Pose",
            "Warrior 1": "Warrior_I",
            "Warrior 2": "Warrior_II",
            "Warrior 3": "Warrior_III"
        }

        # Mode mapping (used in charts)
        self.MODE_MAP = {
            "PRACTICE": 0,
            "EASY": 1,
            "HARD": 2,
        }

        # Posture mapping (record_picture.posture_id)
        self.POSTURE_MAP = {
            "Bridge Pose": 0,
            "Chair Pose": 1,
            "Downward Facing Dog": 2,
            "Locust Pose": 3,
            "Plank Pose": 4,
            "Staff Pose": 5,
            "Triangle Pose": 6,
            "Warrior 1": 7,
            "Warrior 2": 8,
            "Warrior 3": 9,
        }

        # Default dates = today
        today = datetime.today().date()
        self.dateEdit.setDate(today)
        self.dateEdit_2.setDate(today)

        # -----------------------------
        # CHART BUTTON + DATA
        # -----------------------------
        self.pushButton_6.clicked.connect(self.generate_score_plot)
        self.chart_groups = []
        self.chart_paths = []
        self.current_group_index = 0
        self.pushButton.clicked.connect(self.show_prev_group)
        self.pushButton_2.clicked.connect(self.show_next_group)

        # Share input placeholder
        self.plainTextEdit.setPlaceholderText("請輸入貼文內容...")
        self.pushButton_3.clicked.connect(self.on_share_post_clicked)

        # Reset inputs on login/logout
        self.account.user_id_signal.connect(self.reset_share_input)
        self.account.user_id_signal.connect(self.reset_chart_and_dates)
        self.account.user_id_signal.connect(self.countdown_timer.reset_timer)

        # Reset button logic
        self.rst_btn.clicked.connect(self.on_reset_clicked)

        # -----------------------------
        # Buffers for recording pose data
        # -----------------------------
        self.pose_record_buffer = []     # per-second pose data
        self.pose_accuracy_buffer = []   # accuracy for each pose
        self.stats_buffer = {}           # reduce DB load

        # Variables for bone drawing
        self.result = None
        self.valid_score = True
        self.score_dict = {}

        # connect tab change signal
        self.tabWidget.currentChanged.connect(self.on_tab_changed)

    # Store scoring result from PoseCalculate
    def set_draw_bone_variable(self, score_dict, result):
        self.result = result
        self.score_dict = score_dict

    # Navigation with login checking
    def navigate_with_auth(self, index, checked, button):
        if not checked:
            return

        # Pages that require login
        if index not in [1, 5] and not self.account.login_flag:
            NotificationLabel(self, "Please login first to unlock the features.", success=False)
            button.setChecked(False)
            return

        # If switching page, turn off the camera
        if self.stackedWidget.currentIndex() != 0:
            self.on_camera_btn_toggled()

        self.stackedWidget.setCurrentIndex(index)

    # Window dragging behavior for frameless UI
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

    # Receive new frame from CameraThread
    def update_current_frame(self, frame):
        self.detector.frame = frame
        self.gesture_analyzer.frame = frame
  
    def update_GUI_frame(self, processed_frame):
        if not processed_frame is None:
            try:
                if self.result and not self.valid_score and self.score_dict:
                    draw_frame=self.critical_bone.process(self.score_dict,self.result,processed_frame)
                    processed_frame=draw_frame
                else:
                    pass
            except Exception as e:
                print("draw critical bone error:", e)
                
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_label.setPixmap(pixmap)
        else:
            # blank = np.zeros_like(self.prev_frame) if hasattr(self, "prev_frame") else None
            # self._show_frame(blank)
            return
    
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
                if self.countdown_timer.initial:
                    self.countdown_timer._stop_timer()
                    if self.countdown_timer.startup_timer.isActive() and self.countdown_timer.is_first_startup:
                        self.countdown_timer._reset_startup_state()
                    elif self.countdown_timer.startup_timer.isActive():
                        self.countdown_timer._reset_partially_startup_state()
                self.countdown_timer.camera_is_running = False

                QTimer.singleShot(100, lambda: self.clear_camera_label())
                NotificationLabel(self, "Camera closed", success=False)
                

        elif not self.account.login_flag:
            self.camera_btn.setChecked(False)
            # NotificationLabel(self, "Please login first to unlock all features.", success=False)
        
    def clear_camera_label(self):
        self.camera_label.setPixmap(QPixmap())
        self.camera_label.setText('Lens screen not found')
            
    def show_share_page_widget(self):
        self.frame_12.show()
    
    def toggle_share_comment_widget(self):
        if self.share_comment_frame.isVisible():
            self.share_comment_frame.hide()
        else:
            self.share_comment_frame.show()
    
    def hide_share_page_widget(self):
        self.frame_12.hide()
        self.post_dialog.reset_post_fields()
    
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
        self.update_GUI_frame(self.detector.frame)
        
    def previous_pose(self, skip_flag):
        print('Prvious Pose')
        if not hasattr(self, 'image_list') or not self.image_list:
            QMessageBox.warning(self, 'Error', 'No images to display. Please load images first.')
            return
        
        if self.countdown_timer.timer_is_running:
            self.countdown_timer.skip(skip_flag)

        self.image_index = (self.image_index - 1) % len(self.image_list)
        self.display_image(self.image_list[self.image_index])
        self.update_GUI_frame(self.detector.frame)
    
    def toggle_touch_note(self, str):
        self.gesture_analyzer.enabled = not self.gesture_analyzer.enabled
        if self.gesture_analyzer.enabled:
            NotificationLabel(self, f"Gesture control enabled", success=True)
        else:    
            NotificationLabel(self, f"Gesture control disabled", success=False)

    #connect to database
    # def connect_db(self):
    #     try:
    #         db = pymysql.connect(
    #             host='127.0.0.1',
    #             user='root',
    #             password='root123456',
    #             database='yoga_coach_database',
    #             port=3306,
    #             cursorclass=pymysql.cursors.DictCursor
    #         )
    #         print("pymysql connected successfully")
    #         return db
    #     except Exception as e:
    #         print("pymysql connection error: ", e)
    def connect_db(self):
        try:
            db = pymysql.connect(
                host='26.205.73.65',
                user='yoga_app',
                password='yoga_app123456',
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
        """Perform pose detection, scoring, and save results with countdown and timestamp."""

        # -----------------------------
        # 1️ If the app is paused or not active, flush buffers
        # -----------------------------
        current_state = self.state_reg_label.text()

        if current_state != "Exercise":
            if current_state in ["Pause", "N/A"]:
                self.flush_pose_buffer()  
                self.countdown_timer.on_pose_detected(False)
                return

            self.countdown_timer.on_pose_detected(False)
            return

        # -----------------------------
        # 2️ Skip if frame, detector, or camera not ready
        # -----------------------------
        if (not hasattr(self, 'current_pose_index') or 
            not getattr(self.detector, "yolo_has_person", False) or 
            not self.countdown_timer.camera_is_running or 
            self.detector.frame is None):
            self.countdown_timer.on_pose_detected(False)
            return

        # -----------------------------
        # 3️ Skip if no demo pose selected
        # -----------------------------
        current_demo_item = self.demo_list.currentItem()
        if current_demo_item is None:
            self.countdown_timer.on_pose_detected(False)
            return

        selected_display_name = current_demo_item.text().strip()
        selected_pose_name = self.pose_name_map.get(selected_display_name)
        detected_pose_name = self.detector.pose_names[self.current_pose_index]

        # -----------------------------
        # 4️ Skip if detected pose doesn't match selected demo pose
        # -----------------------------
        if selected_pose_name is None or detected_pose_name != selected_pose_name:
            self.countdown_timer.on_pose_detected(False)
            return

        # -----------------------------
        # 5️ Evaluate pose score using PoseCalculate
        # -----------------------------
        try:
            text, avg = self.pose_calculator.evaluate_pose(
                self.detector.frame,
                self.current_pose_index,
                self.pose_reg_label
            )
        except Exception as e:
            avg = None
        
        if avg and avg > 0.0:
            mode = self.countdown_timer.mode
            ts = datetime.now()

            # Update standard score display for this pose
            display_standard_score(self.standard_score, detected_pose_name, mode)

            font = QFont("Arial", 14)         # Set font style and size
            self.pose_reg_label.setFont(font)               # Apply font to widget
            self.pose_reg_label.setPlainText(text)

            # -----------------------------
            # 7️ Buffer pose accuracy updates (do not write to DB immediately)
            # -----------------------------
            try:
                self.valid_score = is_pose_score_valid(self.current_pose_index, avg, mode)
                if self.valid_score:

                    # Ensure countdown timer is running
                    if not self.countdown_timer.timer.isActive():
                        self.countdown_timer.timer.start(1000)
                    
                    countdown_value = self.countdown_timer.get_remaining_seconds()
                    self.pose_record_buffer.append({
                        "posture_id": self.current_pose_index,
                        "posture_name": detected_pose_name,
                        "accuracy": avg,
                        "mode": mode,
                        "countdown": countdown_value,
                        "timestamp":ts
                    })
                    self.pose_accuracy_buffer.append({
                        "posture_id": self.current_pose_index,
                        "posture_name": detected_pose_name,
                        "mode": mode,
                        "accuracy": avg
                    })
                else:  
                    # If score invalid and mode is challenging → pause timer
                    if mode in ["Easy", "Hard"]:
                        if self.countdown_timer.timer.isActive():
                            self.countdown_timer.timer.stop()
                            NotificationLabel(self, "Score below threshold! Timer paused.", success=False)
            except Exception as e:
                print("is_pose_score_valid error:", e)
        elif self.countdown_timer.mode in ["Easy", "Hard"]:
            if self.countdown_timer.timer.isActive():
                self.countdown_timer.timer.stop()
                NotificationLabel(self, "Timer paused.", success=False)
        elif avg is None:
            font = QFont("Arial", 12)         # Set font style and size
            self.pose_reg_label.setFont(font)               # Apply font to widget
            self.pose_reg_label.setPlainText("Pose detected but no landmarks")


        # -----------------------------
        # 8️ Notify countdown timer whether a pose was detected
        # -----------------------------
        
    
    def wakeup_timer(self):
        """Check if the countdown timer has stopped; if so, flush buffers."""
        if not self.countdown_timer.timer.isActive():
            self.perform_pose_scoring()


    def update_progress_page_statistics(self, mode, force_refresh=False):
        """Cache statistics; only update UI when force_refresh=True."""
        try:
            # use cached stats unless force refresh
            if not force_refresh and mode in self.stats_buffer:
                stats = self.stats_buffer[mode]['stats']
                stats_all = self.stats_buffer[mode]['stats_all']
            else:
                stats = self.logger.load_statistics(mode)
                stats_all = self.logger.load_statistics("ALL")
                self.stats_buffer[mode] = {'stats': stats, 'stats_all': stats_all}
        except Exception as e:
            print("update_progress_page_statistics load_statistics error:", e)
            return

        # skip UI update if not forced
        if not force_refresh:
            return

        # --- update overall stats ---
        if stats_all:
            self.label_18.setText(str(stats_all["total_count"]))
            usage = stats_all.get("usage", {})
            total_usage_days = usage.get("total_usage_days", 0.0)
            self.label_21.setText(f"{total_usage_days:.4f}")
            self.label_29.setText(str(usage.get("daily_max_app_opens", 0)))
            self.label_73.setText(f"{usage.get('max_daily_usage_hours', 0.0):.4f}")
            self.label_75.setText(f"{usage.get('min_daily_usage_hours', 0.0):.4f}")
            self.label_27.setText(str(usage.get("longest_streak_days", 0)))

        # --- update pose stats ---
        if stats:
            max_pose_name, max_pose_count = stats.get("max_pose", (None, 0))
            min_pose_name, min_pose_count = stats.get("min_pose", (None, 0))
            self.label_23.setText(str(max_pose_name or ""))
            self.label_31.setText(str(max_pose_count or 0))
            self.label_25.setText(str(min_pose_name or ""))
            self.label_32.setText(str(min_pose_count or 0))

            counts = stats.get("counts", {})
            per_acc = stats.get("per_pose_accuracy", {})
            for pose in self.logger.pose_names:
                cnt = counts.get(pose, 0)
                accs = per_acc.get(pose, {})
                max_a = accs.get("max")
                min_a = accs.get("min")
                count_lbl, max_lbl, min_lbl = self.logger.pose_labels.get(pose, (None, None, None))
                if count_lbl:
                    count_lbl.setText(str(cnt))
                if max_lbl:
                    max_lbl.setText(f"{max_a:.1f}" if max_a is not None else "0")
                if min_lbl:
                    min_lbl.setText(f"{min_a:.1f}" if min_a is not None else "0")

    def on_mode_changed(self, mode_name):
        """Refresh UI only when mode changes."""
        self.label_16.setText(mode_name)
        try:
            # refresh UI using cached stats
            self.update_progress_page_statistics(mode_name, force_refresh=True)
        except Exception as e:
            print("on_mode_changed error:", e)
    
    def on_tree_item_changed(self, item, column):
        """
        Detect changes in treewidget column 1, use snapshot to calculate delta and update record_detail.
        Only increment when the number increases (supports delta > 1).
        """
        if column != 1:
            return
        try:
            idx = self.countdown_timer.statistics_treewidget.indexOfTopLevelItem(item)
            if idx < 0:
                return

            txt = item.text(1).strip() if item.text(1) else "0"
            new_count = int(txt) if txt.isdigit() else 0

            # Get previous snapshot
            old_count = 0
            if idx < len(self._tree_counts_snapshot):
                old_count = self._tree_counts_snapshot[idx]
            delta = new_count - old_count

            if delta > 0:
                # Incremental write (without accuracy, because counts come from the treewidget)
                self.logger.increment_pose_count(
                    posture_id=idx,
                    posture_name=self.logger.pose_names[idx],
                    mode=self.countdown_timer.mode,
                    delta=delta
                )

            # Update snapshot (sync to latest)
            if idx < len(self._tree_counts_snapshot):
                self._tree_counts_snapshot[idx] = new_count
            else:
                # If the snapshot is shorter, extend it
                extend_len = idx - len(self._tree_counts_snapshot) + 1
                self._tree_counts_snapshot.extend([0] * extend_len)
                self._tree_counts_snapshot[idx] = new_count

        except Exception as e:
            print("on_tree_item_changed error:", e)

    def on_prev_mode(self):
        current = self.difficulties.index(self.label_16.text())
        new_mode = self.difficulties[(current - 1) % len(self.difficulties)]
        self.on_mode_changed(new_mode)

    def on_next_mode(self):
        current = self.difficulties.index(self.label_16.text())
        new_mode = self.difficulties[(current + 1) % len(self.difficulties)]
        self.on_mode_changed(new_mode)

    def closeEvent(self, event):
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.end_session()
        except Exception:
            pass
        super().closeEvent(event)
    
    def generate_score_plot(self):
        """
        Generate grouped charts using generate_chart.fetch_and_group_data and save_group_charts.
        If no DB groups found, try to find existing images in record_pic folder by filename prefix.
        After generation / loading, set self.chart_paths and display the first image.
        """
        if not self.account.user_id:
            NotificationLabel(self, "Please login first.", success=False)
            return

        user_id = self.account.user_id
        mode_text = self.comboBox_3.currentText().upper()  # PRACTICE/EASY/HARD
        posture_text = self.comboBox.currentText()
        start_date = self.dateEdit.date().toPyDate()
        end_date = self.dateEdit_2.date().toPyDate()

        # Basic validation
        if start_date > end_date:
            QMessageBox.warning(self, "Invalid Date Range", "Start date must be <= end date.")
            return

        try:
            # fetch grouped small groups
            groups = generate_chart.fetch_and_group_data(
                user_id=user_id,
                mode_text=mode_text,
                posture_text=posture_text,
                db=self.db,
                start_date=start_date,
                end_date=end_date
            )

            if not groups:
                NotificationLabel(self, "No data found for the selected date range.", success=False)
                self.chart_groups = []
                self.chart_paths = []
                self.current_group_index = 0
                return

            # Save charts for each small group (this will create/overwrite image files)
            paths = generate_chart.save_group_charts(groups, self.account.user_id, posture_text, mode_text)

            if not paths:
                NotificationLabel(self, "No data found.", success=False)
                self.chart_groups = []
                self.chart_paths = []
                self.current_group_index = 0
                return

            self.chart_groups = groups
            self.chart_paths = paths
            self.current_group_index = 0
            self.show_current_group()

            # Send charts to user Discord DM via bot (if linked)
            reply = QMessageBox.question(
                self,
                "Send to Discord DM?",
                "Do you want to send the generated charts to your Discord DM (if linked)?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                sql = "SELECT discord_id FROM discord_users WHERE user_id = %s"
                try:
                    with self.db.cursor() as cursor:
                        cursor.execute(sql, (user_id,))
                        result = cursor.fetchone()
                        if result and result.get("discord_id"):
                            discord_id = result['discord_id']
                            sql = "INSERT INTO bot_message_queue (discord_id, mode, posture, start_date, end_date) VALUES (%s, %s, %s, %s, %s)"
                            with self.db.cursor() as cursor:
                                cursor.execute(sql, (discord_id, mode_text, posture_text, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
                                self.db.commit()
                                NotificationLabel(self, "Request sent to Discord bot. Check your DM later.", success=True)
                        else:
                            NotificationLabel(self, "No Discord account linked. Please link your account first.", success=False)    
                except Exception as e:
                    print("Discord DM DB error:", e)
                    NotificationLabel(self, "Database error when sending to Discord bot.", success=False)    
        except Exception as e:
            print("generate_score_plot error:", e)
            NotificationLabel(self, "Error generating chart.", success=False)
            
    def toggle_mode_buttons(self, enabled: bool):
        """Enable or disable mode switch buttons."""
        self.practice_btn.setEnabled(enabled)
        self.easy_btn.setEnabled(enabled)
        self.hard_btn.setEnabled(enabled)
    
    def show_current_group(self):
        """Display the current image from self.chart_paths in label_3."""
        try:
            if not getattr(self, "chart_paths", None):
                return
            if not (0 <= self.current_group_index < len(self.chart_paths)):
                return
            path = self.chart_paths[self.current_group_index]
            pixmap = QPixmap(path)
            if pixmap.isNull():
                NotificationLabel(self, "Failed to load chart image.", success=False)
                return
            self.label_3.setPixmap(pixmap)
            self.label_3.setScaledContents(True)
            NotificationLabel(self, f"Showing {self.current_group_index+1}/{len(self.chart_paths)}", success=True)
        except Exception as e:
            print("show_current_group error:", e)

    def show_prev_group(self):
        """Show previous chart (wrap around)."""
        if not getattr(self, "chart_paths", None):
            return
        self.current_group_index = (self.current_group_index - 1) % len(self.chart_paths)
        self.show_current_group()

    def show_next_group(self):
        """Show next chart (wrap around)."""
        if not getattr(self, "chart_paths", None):
            return
        self.current_group_index = (self.current_group_index + 1) % len(self.chart_paths)
        self.show_current_group()

    def on_share_post_clicked(self):
        """Save post text and chart image (as BLOB) to database when share button is clicked."""
        user_id = self.account.user_id
        if not user_id:
            NotificationLabel(self, "Please login first.", success=False)
            return

        share_text = self.plainTextEdit.toPlainText().strip()

        if not self.chart_paths or not (0 <= self.current_group_index < len(self.chart_paths)):
            NotificationLabel(self, "Please generate a chart before sharing.", success=False)
            return

        chart_path = self.chart_paths[self.current_group_index]
        image_data = None

        try:
            with open(chart_path, "rb") as f:
                image_data = f.read()
        except Exception as e:
            NotificationLabel(self, f"Failed to read image: {e}", success=False)
            return

        try:
            with self.db.cursor() as cursor:
                sql = """
                    INSERT INTO share_page (user_id, share_date, share_text, share_content, share_like)
                    VALUES (%s, NOW(), %s, %s, 0)
                """
                cursor.execute(sql, (user_id, share_text, image_data))
            self.db.commit()

            self.post_dialog.load_posts()

            NotificationLabel(self, "Post shared successfully.", success=True)
            self.plainTextEdit.clear()
            self.plainTextEdit.setPlaceholderText("Enter your post content...")

        except Exception as e:
            print("on_share_post_clicked DB error:", e)
            NotificationLabel(self, f"Database error: {e}", success=False)

    def reset_share_input(self, user_id):
        """Clear PlainTextEdit when user logs in or out."""
        self.plainTextEdit.clear()
        self.plainTextEdit.setPlaceholderText("請輸入貼文內容...")
    
    def reset_chart_and_dates(self, user_id):
        """Reset date fields and clear chart when the user logs out."""
        # If account_status_label shows "Guest" or user_id is None, it means the user has logged out
        if self.account_status_label.text() == "Guest" or not user_id:
            today = datetime.today().date()
            # Reset both date pickers to today's date
            self.dateEdit.setDate(today)
            self.dateEdit_2.setDate(today)
            # Clear the chart display
            self.label_3.clear()
            # Clear temporary chart data
            self.chart_groups = []
            self.chart_paths = []
            self.current_group_index = 0
    
    def on_reset_clicked(self):
        """Handle reset button clicked."""
        try:
            NotificationLabel(self, "Reset successful. Count increased.", success=True)
        except Exception as e:
            print("on_reset_clicked error:", e)
    
    def flush_pose_buffer(self):
        """Upload all buffered data (pose + accuracy) to DB when Exercise ends."""
        try:
            # Upload pose records
            if self.pose_record_buffer:
                for record in self.pose_record_buffer:
                    self.logger.add_picture_record(
                        posture_id=record["posture_id"],
                        posture_name=record["posture_name"],
                        accuracy=record["accuracy"],
                        mode=record["mode"],
                        countdown=record["countdown"],
                        timestamp=record["timestamp"]
                    )
                self.pose_record_buffer.clear()

            # Upload accuracy records
            if getattr(self, "pose_accuracy_buffer", None):
                for acc in self.pose_accuracy_buffer:
                    self.logger.update_pose_accuracy(
                        posture_id=acc["posture_id"],
                        posture_name=acc["posture_name"],
                        mode=acc["mode"],
                        accuracy=acc["accuracy"]
                    )
                self.pose_accuracy_buffer.clear()

        except Exception as e:
            print("flush_pose_buffer error:", e)
    
    def on_tab_changed(self, index):
        # refresh stats when p2 is selected
        if index == 1:
            self.update_progress_page_statistics(self.countdown_timer.mode, force_refresh=True)