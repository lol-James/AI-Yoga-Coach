import cv2
from Ui_AIYogaCoachInterface import Ui_MainWindow
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QPixmap, QIcon
from camera import CameraThread
from yoga_pose_detector import YogaPoseDetector
from musicPlayer import MusicPlayer
from gesture import GestureAnalyzer, GestureInterpreter

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
            self.account_btn: 4, self.full_account_btn: 4, self.info_btn: 5, self.full_info_btn: 5,
            self.login_out_btn: 6, self.full_login_out_btn: 6
        }
        for btn, index in button_index_map.items():
            btn.toggled.connect(lambda checked, i=index: self.stackedWidget.setCurrentIndex(i))
        # camera and yoga detector initializations
        self.camera_thread = CameraThread()
        self.camera_thread.new_frame.connect(self.update_current_frame)
        self.detector = YogaPoseDetector()
        self.detector.result_image_signal.connect(self.update_GUI_frame)
        self.camera_btn.toggled.connect(self.on_camera_btn_toggled)
        #share page
        self.addShareicon.setCheckable(True)
        self.share_comment_btn.setCheckable(True)
        self.share_cancel_btn.setCheckable(True)
        self.widget_6.hide()
        self.share_comment_frame.hide()
        self.addShareicon.clicked.connect(self.show_share_page_widget)
        self.share_comment_btn.clicked.connect(self.toggle_share_comment_widget)
        self.share_cancel_btn.clicked.connect(self.hide_share_page_widget)
        # account
        self.reg_ui.hide()
        self.forgot_ui.hide()
        self.login_register_btn.clicked.connect(self.change_account_widget)
        self.login_forgot_btn.clicked.connect(self.change_account_widget)
        self.reg_back_btn.clicked.connect(self.change_account_widget)
        self.forgot_back_btn.clicked.connect(self.change_account_widget)
        # user info
        self.adjust_password_widget.hide()
        self.adjust_information_widget.hide()
        self.config_password.clicked.connect(self.change_user_info_widget)
        self.config_user_information.clicked.connect(self.change_user_info_widget)
        self.data_change_cancel.clicked.connect(self.change_user_info_widget)
        self.change_password_cancel.clicked.connect(self.change_user_info_widget)
        # Music Player
        self.music_player = MusicPlayer(self)
        # mediapipe gesture analyzer initialization
        self.gesture_analyzer = GestureAnalyzer()
        self.gesture_interpreter = GestureInterpreter(self)
        self.gesture_analyzer.result_str_signal.connect(self.gesture_interpreter.interpret)
        self.show()
            
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
        """Update image on GUI app"""
        if not processed_frame is None:
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_label.setPixmap(pixmap)
    
    def on_camera_btn_toggled(self):
        if self.camera_btn.isChecked():
            self.camera_thread.start()
            self.detector.start()
            self.gesture_analyzer.start()
        else:
            self.camera_thread.stop()
            self.detector.stop()
            self.gesture_analyzer.stop()
            QTimer.singleShot(100, lambda: self.clear_camera_label())
        
    def clear_camera_label(self):
        self.camera_label.setPixmap(QPixmap())
        self.camera_label.setText('Lens screen not found')
    
    def change_account_widget(self):
        if self.login_register_btn.isChecked():
            self.login_ui.hide()
            self.reg_ui.show()
            self.login_register_btn.setChecked(False)
        if self.login_forgot_btn.isChecked():
            self.login_ui.hide()
            self.forgot_ui.show()
            self.login_forgot_btn.setChecked(False)
        if self.reg_back_btn.isChecked():
            self.reg_ui.hide()
            self.login_ui.show()
            self.reg_back_btn.setChecked(False)
        if self.forgot_back_btn.isChecked():
            self.forgot_ui.hide()
            self.login_ui.show()
            self.forgot_back_btn.setChecked(False)
    
    def change_user_info_widget(self):
        if self.config_password.isChecked():
            self.user_information_widget.hide()
            self.adjust_password_widget.show()
            self.config_password.setChecked(False)
            
        if self.config_user_information.isChecked():
            self.user_information_widget.hide()
            self.adjust_information_widget.show()
            self.config_user_information.setChecked(False)
            
        if self.data_change_cancel.isChecked():
            self.adjust_information_widget.hide()
            self.user_information_widget.show()
            self.data_change_cancel.setChecked(False)
            
        if self.change_password_cancel.isChecked():
            self.adjust_password_widget.hide()
            self.user_information_widget.show()
            self.change_password_cancel.setChecked(False)
            
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

    def next_pose(self):
        print('Next Pose')
        
    def previous_pose(self):
        print('Prvious Pose')