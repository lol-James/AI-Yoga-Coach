import os
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime
from PyQt5.QtCore import Qt, QPoint, QUrl, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QImage, QMouseEvent, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import cv2

from camera import CameraThread
from yoga_pose_detector import YogaPoseDetector

from Ui_AIYogaCoachInterface import Ui_MainWindow

class AIYogaCoachApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # gui initialization
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.maximize_btn.setCheckable(True)
        self.ui.maximize_btn.clicked.connect(self.toggle_maxmize_btn)
        self.ui.minimize_btn.clicked.connect(self.showMinimized)
        self.ui.close_btn.clicked.connect(self.close)
        self.old_pos = self.pos()
        self.mouse_pressed = False
        self.ui.full_menu_frame.setHidden(True)
        self.ui.full_home_btn.setCheckable(True)
        self.ui.home_btn.toggled.connect(self.on_home_btn_toggled)
        self.ui.full_home_btn.toggled.connect(self.on_full_home_btn_toggled)
        self.ui.music_btn.toggled.connect(self.on_music_btn_toggled)
        self.ui.full_music_btn.toggled.connect(self.on_full_music_btn_toggled)
        self.ui.progress_btn.toggled.connect(self.on_progress_btn_toggled)
        self.ui.full_progress_btn.toggled.connect(self.on_full_progress_btn_toggled)
        self.ui.share_btn.toggled.connect(self.on_share_btn_toggled)
        self.ui.full_progress_btn.toggled.connect(self.on_full_progress_btn_toggled)
        self.ui.account_btn.toggled.connect(self.on_account_btn_toggled)
        self.ui.full_account_btn.toggled.connect(self.on_full_account_btn_toggled)
        self.ui.info_btn.toggled.connect(self.on_info_btn_toggled)
        self.ui.full_info_btn.toggled.connect(self.on_full_info_btn_toggled)

        # camera and yoga detector initializations
        self.camera_thread = CameraThread()
        self.camera_thread.new_frame.connect(self.update_current_frame)
        self.detector = YogaPoseDetector()
        self.detector.result_image_signal.connect(self.update_GUI_frame)
        self.ui.camera_btn.toggled.connect(self.on_camera_btn_toggled)

        # account
        self.ui.reg_ui.hide()
        self.ui.forgot_ui.hide()
        self.ui.login_register_btn.clicked.connect(self.change_account_widget)
        self.ui.login_forgot_btn.clicked.connect(self.change_account_widget)
        self.ui.reg_back_btn.clicked.connect(self.change_account_widget)
        self.ui.forgot_back_btn.clicked.connect(self.change_account_widget)

        self.show()
        
        
    def toggle_maxmize_btn(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def mousePressEvent(self, event):
        if self.ui.title_frame.underMouse():  
            self.old_pos = event.globalPos()
            self.mouse_pressed = True

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
            
    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False
    
    def on_home_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)
    
    def on_full_home_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(0)
        
    def on_music_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        
    def on_full_music_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(1)
    
    def on_progress_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)

    def on_full_progress_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        
    def on_share_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)

    def on_full_progress_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(3)
        
    def on_account_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    def on_full_account_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(4)

    def on_info_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(5)

    def on_full_info_btn_toggled(self):
        self.ui.stackedWidget.setCurrentIndex(5)

    def update_current_frame(self, frame):
        self.detector.frame = frame
    
    def update_GUI_frame(self, processed_frame):
        """Update image on GUI app"""
        if not processed_frame is None:
            rgb_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.ui.camera_label.setPixmap(pixmap)
    
    def on_camera_btn_toggled(self):
        if self.ui.camera_btn.isChecked():
            self.camera_thread.start()
            self.detector.start()
        else:
            self.camera_thread.stop()
            self.detector.stop()
            QTimer.singleShot(100, lambda: self.clear_camera_label())
        
    def clear_camera_label(self):
        self.ui.camera_label.setPixmap(QPixmap())
        self.ui.camera_label.setText('Lens screen not found')
    
    def change_account_widget(self):
        if self.ui.login_register_btn.isChecked():
            self.ui.login_ui.hide()
            self.ui.reg_ui.show()
            self.ui.login_register_btn.setChecked(False)
        if self.ui.login_forgot_btn.isChecked():
            self.ui.login_ui.hide()
            self.ui.forgot_ui.show()
            self.ui.login_forgot_btn.setChecked(False)
        if self.ui.reg_back_btn.isChecked():
            self.ui.reg_ui.hide()
            self.ui.login_ui.show()
            self.ui.reg_back_btn.setChecked(False)
        if self.ui.forgot_back_btn.isChecked():
            self.ui.forgot_ui.hide()
            self.ui.login_ui.show()
            self.ui.forgot_back_btn.setChecked(False)
    