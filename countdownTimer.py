from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtWidgets import QMessageBox, QDialog, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, QPushButton
from PyQt5.QtGui import QIntValidator, QIcon
from collections import deque
from notification import NotificationLabel
class Timer(QThread):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        # UI Elements Initialization
        self.timer_lcdnumber = self.ui.timer_lcdnumber
        self.set_time_btn = self.ui.set_time_btn
        self.start_btn = self.ui.start_btn
        self.rst_btn = self.ui.rst_btn
        self.state_reg_label = self.ui.state_reg_label
        self.camera_btn = self.ui.camera_btn
        self.practice_btn = self.ui.practice_btn
        self.easy_btn = self.ui.easy_btn
        self.hard_btn = self.ui.hard_btn
        self.mode_selection_label = self.ui.mode_selection_label
        self.statistics_treewidget = self.ui.statistics_treewidget
        self.statistics_treewidget.setColumnWidth(0, 180)  
        self.statistics_treewidget.setColumnWidth(1, 150)  

        # timer
        self.camera_is_running = False
        self.timer_is_running = False
        self.initial = False
        self.three_sec_startup = False

        self.default_exercise_time = 15000
        self.default_rest_time = 10000
        self.exercise_time = self.default_exercise_time
        self.rest_time = self.default_rest_time
        self.states = ['Exercise', 'Rest', 'Pause', 'N/A']
        self.state_index = 1 
        self.state = self.states[3]
        self.record = [0 for _ in range(10)]
        self.update_lcdnumber()

        # init timer
        self.timer = QTimer(self.ui)
        self.timer.timeout.connect(self.update_timer)
        self.set_time_btn.clicked.connect(self.set_timer)
        self.start_btn.clicked.connect(self.toggled_start_pause_timer)
        self.rst_btn.clicked.connect(self.reset_timer)

        # mode selection
        self.mode = None
        self.practice_btn.clicked.connect(self.mode_selection)
        self.easy_btn.clicked.connect(self.mode_selection)
        self.hard_btn.clicked.connect(self.mode_selection)


        # pose history
        self.pose_history = deque(maxlen=3)

    def update_lcdnumber(self):
        if self.state == 'Rest' or self.state == 'N/A' or (self.state_index == 1 and self.timer_is_running):
            self.min = str((self.rest_time // 1000) // 60)
            self.sec = str((self.rest_time // 1000) % 60)
        else:
            self.min = str((self.exercise_time // 1000) // 60)
            self.sec = str((self.exercise_time // 1000) % 60)
        
        self.min = '0' + str(self.min)
        if len(self.sec) == 1:
            self.sec = '0' + str(self.sec)
        else:
            self.sec = str(self.sec)

        self.timer_lcdnumber.display(self.min + ':' + self.sec)

    def update_timer(self):
        if self.state == 'Exercise':
            if self.exercise_time == 0:
                self.state_index = 1 
                self.state = self.states[1]
                self.state_reg_label.setText(self.state)
                self.exercise_time = self.default_exercise_time

                self.record[self.ui.image_index] += 1
                self.statistics_treewidget.topLevelItem(self.ui.image_index).setText(1, str(self.record[self.ui.image_index]))
                self.ui.next_pose(False)
            else:
                self.exercise_time -= 1000
        elif self.state == 'Rest':
            if self.rest_time == 0:
                self.state_index = 0
                self.state = self.states[0]
                self.state_reg_label.setText(self.state)
                self.rest_time = self.default_rest_time
            else:
                self.rest_time -= 1000
        self.update_lcdnumber()

    def show_setting_dialog(self):
        dialog = QDialog(self.ui)
        dialog.setWindowTitle("Setting Timer")

        exercise_input = QLineEdit()
        exercise_input.setValidator(QIntValidator(5, 60))
        exercise_input.setPlaceholderText("Sec")

        rest_input = QLineEdit()
        rest_input.setValidator(QIntValidator(5, 120))
        rest_input.setPlaceholderText("Sec")

        exercise_input.setText(str(self.default_exercise_time // 1000))
        rest_input.setText(str(self.default_rest_time // 1000))

        layout = QFormLayout()
        layout.addRow("Exercise time per pose: ", exercise_input)
        layout.addRow("Rest time per pose: ", rest_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        def on_accept():
            try:
                ex_val = int(exercise_input.text())
                rt_val = int(rest_input.text())
                if not (5 <= ex_val <= 60 and 5 <= rt_val <= 120):
                    raise ValueError
                self.default_exercise_time = ex_val * 1000
                self.default_rest_time = rt_val * 1000
                self.exercise_time = self.default_exercise_time
                self.rest_time = self.default_rest_time
                self.update_lcdnumber()
                dialog.accept()
            except:
                QMessageBox.warning(dialog, "Invalid Input", "Please enter valid values:\nExercise: 5~60 sec\nRest: 5~120 sec")

        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(dialog.reject)

        dialog.exec_()

    def set_timer(self):
        if not self.timer_is_running:
            self.show_setting_dialog()


    def toggled_start_pause_timer(self):
        if not self.initial and self.camera_is_running:
            self.initial = True
            self.ui.reset_to_first_image()

        if not self.three_sec_startup and self.camera_is_running:
            self.set_time_btn.setEnabled(False)
            self.start_btn.setEnabled(False)
            self.rst_btn.setEnabled(False)
            self.three_sec_startup = True
            self.state_reg_label.setText("Ready...")
            QTimer.singleShot(1000, lambda: self.state_reg_label.setText("3"))
            QTimer.singleShot(2000, lambda: self.state_reg_label.setText("2"))
            QTimer.singleShot(3000, lambda: self.state_reg_label.setText("1"))
            QTimer.singleShot(4000, self._start_timer)

        elif self.camera_is_running:
            if not self.timer_is_running:
                self._start_timer()
            else:
                self._stop_timer()
        else:
            QMessageBox.warning(self.ui, "Error", "Please turn on the camera first!")

    def _start_timer(self):
        self.start_btn.setEnabled(True)
        self.rst_btn.setEnabled(True)
        self.state = self.states[self.state_index]
        self.state_reg_label.setText(self.state)
        self.timer_is_running = True
        self.timer.start(1000)
        self.start_btn.setText('Stop')
        self.start_btn.setIcon(QIcon("icons/icons8-pause-60.png"))
        self.start_btn.setIconSize(QSize(20, 20))

    def _stop_timer(self):
        self.state = self.states[2]
        self.state_reg_label.setText(self.state)
        self.timer_is_running = False
        self.timer.stop()
        self.start_btn.setText('Start')
        self.start_btn.setIcon(QIcon("icons/icons8-start-60.png"))
        self.start_btn.setIconSize(QSize(20, 20))
        self.three_sec_startup = False

    def on_pose_detected(self, isUpdated: bool):
        self.pose_history.append(isUpdated)
        # print(f'isUpdated:{isUpdated}')
        # print(f'pose_history{list(self.pose_history)}')

        if self.state == "Exercise" and self.timer_is_running: 
            if not self.timer.isActive():  
                self.timer.start(1000)  
            if not any(self.pose_history):  
                self.timer.stop()
                NotificationLabel(self.ui, "Mediapipe detection failure", success=False,duration=500)

    def reset_timer(self):
        self.state = self.states[3]
        self.state_index = 1
        self.state_reg_label.setText(self.state)
        self.timer_is_running = False
        self.three_sec_startup = False
        self.timer.stop()
        self.start_btn.setText('Start')
        self.start_btn.setIcon(QIcon("icons/icons8-start-60.png"))
        self.start_btn.setIconSize(QSize(20, 20))
        self.set_time_btn.setEnabled(True)
        self.exercise_time = self.default_exercise_time
        self.rest_time = self.default_rest_time
        self.update_lcdnumber()
        self.set_time_btn.setEnabled(True)
        self.initial = False
        self.ui.reset_to_first_image()
        self.record = [0 for _ in range(10)]
        for index, value in enumerate(self.record):
            self.statistics_treewidget.topLevelItem(index).setText(1, str(value))

    def skip(self, skip_flag):
        if skip_flag:
            self.state_index = 1
            self.state = self.states[self.state_index]
            self.state_reg_label.setText(self.state)
            self.exercise_time = self.default_exercise_time
            self.rest_time = self.default_rest_time
            self.update_lcdnumber()
            self.timer.stop()
            self.timer.start(1000)
    
    def mode_selection(self):
        if self.practice_btn.isChecked():
            self.mode = "Practice"
        elif self.easy_btn.isChecked():
            self.mode = "Easy"
        elif self.hard_btn.isChecked():
            self.mode = "Hard"
        self.mode_selection_label.setText(f"Mode Selection: {self.mode}")