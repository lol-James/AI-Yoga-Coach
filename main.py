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

        # record logger (MODIFIED: session handling)
        self.logger = RecordLogger(ui=self, db=self.db)

        # keep record_detail prepared when account emits user_id
        self.account.user_id_signal.connect(self.logger.set_user_id)

        # start a session when login (uid truthy) and end session when logout (uid falsy)
        # pass current mode into start_session so session row has mode assigned
        self.account.user_id_signal.connect(
            lambda uid: self.logger.start_session(self.countdown_timer.mode) if uid else self.logger.end_session()
        )

        # existing connections (keep these)
        self.account.user_id_signal.connect(lambda uid: self.update_progress_page_statistics(self.countdown_timer.mode))
        self.account.user_id_signal.connect(self.user_info.on_signal_received)
        self.account.user_id_signal.connect(self.music_player.update_user_id)
        self.account.user_id_signal.connect(self.post_dialog.update_user_id)
        self.user_info.del_user_account_signal.connect(self.account.logout)

        # Initialize snapshot (record the number of each posture of the current treewidget)
        self._tree_counts_snapshot = []
        for i in range(len(self.logger.pose_names)):
            item = self.countdown_timer.statistics_treewidget.topLevelItem(i)
            try:
                v = int(item.text(1)) if item and item.text(1).isdigit() else 0
            except Exception:
                v = 0
            self._tree_counts_snapshot.append(v)

        # Connect itemChanged event (this handler calculates delta based on snapshot)
        self.countdown_timer.statistics_treewidget.itemChanged.connect(self.on_tree_item_changed)

        # default mode label
        self.label_16.setText("Practice")

        # keep label_16 in sync with selected mode
        self.practice_btn.clicked.connect(lambda: self.on_mode_changed("Practice"))
        self.easy_btn.clicked.connect(lambda: self.on_mode_changed("Easy"))
        self.hard_btn.clicked.connect(lambda: self.on_mode_changed("Hard"))
        self.difficulties = ["Practice", "Easy", "Hard"]
        self.pushButton_7.clicked.connect(self.on_prev_mode)
        self.pushButton_8.clicked.connect(self.on_next_mode)

        # Lock/unlock mode buttons when timer starts/stops
        self.countdown_timer.timer_started_signal.connect(lambda: self.toggle_mode_buttons(False))
        self.countdown_timer.timer_stopped_signal.connect(lambda: self.toggle_mode_buttons(True))

        # calculate score and display
        self.detector.result_pose_signal.connect(self.cache_pose_index)
        self.pose_score_timer = QTimer()
        self.pose_score_timer.timeout.connect(self.perform_pose_scoring)
        self.pose_score_timer.start(500)  

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

        # Mode & posture mapping (for chart usage)
        self.MODE_MAP = {
            "PRACTICE": 0,
            "EASY": 1,
            "HARD": 2,
        }

        # Corresponds to record_picture.posture_id, order must match pose_names (index 0..9)
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

        # pushButton_6
        self.pushButton_6.clicked.connect(self.generate_score_plot)
        self.chart_groups = []
        self.chart_paths = []
        self.current_group_index = 0
        self.pushButton.clicked.connect(self.show_prev_group)
        self.pushButton_2.clicked.connect(self.show_next_group)
    
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

        try:
            # Only refresh the statistics page display, do not call update_detail_from_tree again
            self.update_progress_page_statistics(self.countdown_timer.mode)
        except Exception as e:
            print("update_progress_page_statistics error:", e)
        
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
        # If any of the required preconditions is not met, inform the timer that no pose is detected.
        if not hasattr(self, 'current_pose_index') or not getattr(self.detector, "yolo_has_person", False) \
            or not self.countdown_timer.camera_is_running or self.state_reg_label.text() != "Exercise" \
            or self.detector.frame is None:
            self.countdown_timer.on_pose_detected(False)
            return

        current_demo_item = self.demo_list.currentItem()
        if current_demo_item is None:
            self.countdown_timer.on_pose_detected(False)
            return

        selected_display_name = current_demo_item.text().strip()
        selected_pose_name = self.pose_name_map.get(selected_display_name)
        detected_pose_name = self.detector.pose_names[self.current_pose_index]

        # If the displayed demo pose does not match the detected pose, treat as no pose.
        if selected_pose_name is None or detected_pose_name != selected_pose_name:
            self.countdown_timer.on_pose_detected(False)
            return

        # Evaluate pose and get average score
        avg = evaluate_and_display_pose(
            self.detector.frame,
            self.current_pose_index,
            self.pose_reg_label
        )

        detected = False   # whether a valid pose score was produced (keep timer running)
        updated = False    # whether historical stats need updating (max/min accuracy)

        if avg and avg > 0:
            detected = True  # pose successfully detected and scored

            mode = self.countdown_timer.mode  # "Practice", "Easy", or "Hard"

            # Save the per-second score into record_picture
            try:
                self.logger.add_picture_record(
                    posture_id=self.current_pose_index,
                    posture_name=detected_pose_name,
                    accuracy=avg,
                    mode=mode
                )
            except Exception as e:
                print("add_picture_record error:", e)

            # If the current score passes threshold, update historical max/min accuracy only.
            # Do NOT update completion counts here (counts are driven by statistics_treewidget).
            try:
                if is_pose_score_valid(self.current_pose_index, avg, mode):
                    updated = True
                    try:
                        # Update historical max/min accuracy (do not change completion counts)
                        try:
                            self.logger.update_pose_accuracy(
                                posture_id=self.current_pose_index,
                                posture_name=detected_pose_name,
                                mode=mode,
                                accuracy=avg
                            )
                        except Exception as e:
                            print("update_pose_accuracy error:", e)

                        # Only refresh UI (counts are driven by treewidget)
                        try:
                            self.update_progress_page_statistics(mode)
                        except Exception as e:
                            print("update_progress_page_statistics error:", e)
                    except Exception as e:
                        print("is_pose_score_valid inner error:", e)
            except Exception as e:
                print("is_pose_score_valid error:", e)

        # Pass 'detected' to timer to indicate whether Mediapipe detection succeeded.
        self.countdown_timer.on_pose_detected(detected)

    def update_progress_page_statistics(self, mode):
        try:
            stats = self.logger.load_statistics(mode)
            stats_all = self.logger.load_statistics("ALL")  # ALL mode
        except Exception as e:
            print("update_progress_page_statistics load_statistics error:", e)
            stats = None
            stats_all = None

        # --- Overall statistics across all modes ---
        if stats_all:
            self.label_18.setText(str(stats_all["total_count"]))
            usage = stats_all.get("usage", {})
            # Display total usage **in days, with 4 decimal places**
            total_usage_days = usage.get("total_usage_days")
            if total_usage_days is None:
                # fallback: compute from hours if not present
                try:
                    total_usage_days = round(float(usage.get("total_usage_hours", 0.0) or 0.0) / 24.0, 4)
                except Exception:
                    total_usage_days = 0.0
            self.label_21.setText(f"{total_usage_days:.4f}")

            # Daily max app opens (integer)
            self.label_29.setText(str(usage.get("daily_max_app_opens", 0)))

            # Max/min daily usage hours → show 4 decimal places to avoid rounding short durations to 0.00
            self.label_73.setText(f"{usage.get('max_daily_usage_hours', 0.0):.4f}")
            self.label_75.setText(f"{usage.get('min_daily_usage_hours', 0.0):.4f}")

            # Longest continuous streak
            self.label_27.setText(str(usage.get("longest_streak_days", 0)))

        # --- Pose statistics for the current mode ---
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
        """Update small label when mode button is clicked."""
        self.label_16.setText(mode_name)
        # also refresh progress page stats for this mode
        try:
            self.update_progress_page_statistics(mode_name)
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
                # Update UI display (counts and accuracies)
                try:
                    self.update_progress_page_statistics(self.countdown_timer.mode)
                except Exception:
                    pass

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
        # End session before the application closes (if any)
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.end_session()
        except Exception:
            pass
        super().closeEvent(event)
    
    def generate_score_plot(self):
        """
        Generate grouped charts (each group is a continuous block of seconds).
        """
        if not self.account.user_id:
            NotificationLabel(self, "Please login first.", success=False)
            return

        mode_text = self.comboBox_3.currentText()
        posture_text = self.comboBox.currentText()

        try:
            # fetch grouped data from DB
            groups = generate_chart.fetch_and_group_data(
                user_id=self.account.user_id,
                mode_text=mode_text,
                posture_text=posture_text,
                db=self.db
            )
            if not groups:
                NotificationLabel(self, "No data found.", success=False)
                return

            # save charts for each group
            self.chart_groups = groups
            self.chart_paths = generate_chart.save_group_charts(
                groups, self.account.user_id, posture_text, mode_text
            )
            self.current_group_index = 0

            # display the first group
            self.show_current_group()

        except Exception as e:
            print("generate_score_plot error:", e)
            NotificationLabel(self, "Error generating chart.", success=False)
            
    def toggle_mode_buttons(self, enabled: bool):
        """Enable or disable mode switch buttons."""
        self.practice_btn.setEnabled(enabled)
        self.easy_btn.setEnabled(enabled)
        self.hard_btn.setEnabled(enabled)
    
    def show_current_group(self):
        """Display current group chart in label_3."""
        if not self.chart_paths:
            return
        path = self.chart_paths[self.current_group_index]
        pixmap = QPixmap(path)
        if pixmap.isNull():
            NotificationLabel(self, "Failed to load chart image.", success=False)
            return
        self.label_3.setPixmap(pixmap)
        self.label_3.setScaledContents(True)
        NotificationLabel(self, f"Showing group {self.current_group_index+1}/{len(self.chart_paths)}", success=True)

    def show_prev_group(self):
        if not self.chart_paths:
            return
        self.current_group_index = (self.current_group_index - 1) % len(self.chart_paths)
        self.show_current_group()

    def show_next_group(self):
        if not self.chart_paths:
            return
        self.current_group_index = (self.current_group_index + 1) % len(self.chart_paths)
        self.show_current_group()
