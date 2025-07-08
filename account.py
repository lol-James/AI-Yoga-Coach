from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime
from notification import NotificationLabel
import smtplib
import random
import re

class Account(QObject):
    user_id_signal = pyqtSignal(int)
    def __init__(self, ui, on_camera_btn_toggled):
        super().__init__()
        self.ui = ui
        self.db = ui.db
        self.on_camera_btn_toggled = on_camera_btn_toggled
        self.stackedWidget= self.ui.stackedWidget
        self.account_status_label = self.ui.account_status_label
        
        # widgets intialization
        self.reg_ui = ui.reg_ui
        self.forgot_ui = ui.forgot_ui
        self.login_ui = ui.login_ui
        self.reset_ui = ui.reset_ui
        
        # menu button initialization
        self.login_out_btn = ui.login_out_btn
        self.full_login_out_btn = ui.full_login_out_btn
        self.camera_btn = ui.camera_btn
        
        # ui initialization
        self.reg_ui.hide()
        self.forgot_ui.hide()
        self.reset_ui.hide()
        
        # login ui elements initialization
        self.login_mail_lineedit=ui.login_mail_lineedit
        self.login_password_lineedit=ui.login_password_lineedit
        self.login_forgot_btn = ui.login_forgot_btn
        self.login_btn = ui.login_btn
        self.login_register_btn = ui.login_register_btn
        
        # register ui elements initialization
        self.reg_back_btn = ui.reg_back_btn
        self.reg_register_btn=self.ui.reg_register_btn
        self.reg_firstname_lineedit=self.ui.reg_firstname_lineedit
        self.reg_lastname_lineedit=self.ui.reg_lastname_lineedit
        self.reg_age_lineedit=self.ui.reg_age_lineedit
        self.reg_gender_combobox=self.ui.reg_gender_combobox
        self.reg_mail_lineedit=self.ui.reg_mail_lineedit
        self.reg_password_lineedit=self.ui.reg_password_lineedit
        self.reg_confirm_password_lineedit=self.ui.reg_confirm_password_lineedit

        # forgot password ui elements initialization
        self.forgot_back_btn = ui.forgot_back_btn
        self.forgot_mail_linnedit= self.ui.forgot_mail_lineedit
        self.forgot_send_btn= self.ui.forgot_send_btn
        self.forgot_verification_code_lineedit=self.ui.forgot_verification_code_lineedit
        self.forgot_confirm_btn=self.ui.forgot_confirm_btn

        # reset ui elements initialization
        self.reset_password_lineedit=self.ui.reset_password_lineedit
        self.reset_confirm_password_lineedit=self.ui.reset_confirm_password_lineedit
        self.reset_confirm_btn=self.ui.reset_confirm_btn
        self.reset_back_btn=self.ui.reset_back_btn
        
        # button event
        self.login_register_btn.clicked.connect(self.change_widget)
        self.login_forgot_btn.clicked.connect(self.change_widget)
        self.login_btn.clicked.connect(self.login)
        self.reg_back_btn.clicked.connect(self.change_widget)
        self.reg_register_btn.clicked.connect(self.register)
        self.forgot_back_btn.clicked.connect(self.change_widget)
        self.forgot_send_btn.clicked.connect(self.send_code)
        self.forgot_confirm_btn.clicked.connect(self.verify_code)
        self.reset_back_btn.clicked.connect(self.change_widget)
        self.reset_confirm_btn.clicked.connect(self.reset_password)
        self.login_out_btn.clicked.connect(lambda: self.logout(False))
        self.full_login_out_btn.clicked.connect(lambda: self.logout(False))
        
        # others
        self.user_id = 1
        self.login_flag = False
        self.sent_code = None
        self.sent_email = None
        
    # change account page widget
    def change_widget(self):
        if self.login_register_btn.isChecked():
            self.login_mail_lineedit.clear()
            self.login_password_lineedit.clear()
            self.login_ui.hide()
            self.reg_ui.show()
            self.login_register_btn.setChecked(False)
        if self.login_forgot_btn.isChecked():
            self.login_mail_lineedit.clear()
            self.login_password_lineedit.clear()
            self.login_ui.hide()
            self.forgot_ui.show()
            self.login_forgot_btn.setChecked(False)
        if self.reg_back_btn.isChecked():
            self.reg_firstname_lineedit.clear()
            self.reg_lastname_lineedit.clear()
            self.reg_age_lineedit.clear()
            self.reg_gender_combobox.setCurrentIndex(0)
            self.reg_mail_lineedit.clear()
            self.reg_password_lineedit.clear()
            self.reg_confirm_password_lineedit.clear()
            self.reg_ui.hide()
            self.login_ui.show()
            self.reg_back_btn.setChecked(False)
        if self.forgot_back_btn.isChecked():
            self.forgot_mail_linnedit.clear()
            self.forgot_verification_code_lineedit.clear()
            self.sent_code = None
            self.sent_email = None
            self.forgot_ui.hide()
            self.login_ui.show()
            self.forgot_back_btn.setChecked(False)
        if self.reset_back_btn.isChecked():
            self.reset_password_lineedit.clear()
            self.reset_confirm_password_lineedit.clear()
            self.sent_code = None
            self.sent_email = None
            self.reset_ui.hide()
            self.login_ui.show()
            self.reset_back_btn.setChecked(False)
    
    # form validation about email
    def is_valid_email(self, email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None
    
    # form validation about password
    def is_valid_password(self, password):
        if len(password) < 6:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        return True

    # event handler for login in
    def login(self):
        email = self.login_mail_lineedit.text()
        password = self.login_password_lineedit.text()

        if not email or not password:
            NotificationLabel(self.ui, "All fileds are required.", success=False, duration=3000)
            return
        
        # find email in database
        with self.ui.db.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            
            # the email existent
            if result:
                # check password
                if password == result['user_password']:
                    self.user_id= result['user_id']
                    self.login_flag = True
                    NotificationLabel(self.ui, "Login success", success=True)
                    self.user_id_signal.emit(self.user_id)
                    self.login_mail_lineedit.clear()
                    self.login_password_lineedit.clear()
                    self.stackedWidget.setCurrentIndex(0)
                    self.account_status_label.setText(result['user_account'])
                    self.login_ui.hide()
                else:
                    NotificationLabel(self.ui, "The account or password you entered is incorrect. Please try again.", success=False, duration=3000)
            else:
                NotificationLabel(self.ui, "The account or password you entered is incorrect. Please try again.", success=False, duration=3000)
    
    # event handler for registering a new account
    def register(self):
        firstname = self.reg_firstname_lineedit.text().strip()
        lastname = self.reg_lastname_lineedit.text().strip()
        age = self.reg_age_lineedit.text()
        gender = self.reg_gender_combobox.currentText()
        email = self.reg_mail_lineedit.text()
        password = self.reg_password_lineedit.text()
        confirm_password = self.reg_confirm_password_lineedit.text()
        register_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # form validation
        if not firstname or not lastname or not age or not email or not password or not confirm_password:
            NotificationLabel(self.ui, "All fields are required.", success=False, duration=3000)
            return
        
        if not age.isdigit() or not (1 <= int(age) <= 150):
            NotificationLabel(self.ui, "The age could only be in the range of 1 to 150.", success=False, duration=3000)
            return
        
        if not self.is_valid_email(email):
            NotificationLabel(self.ui, "Invalid email format.", success=False, duration=3000)
            return
        
        if not self.is_valid_password(password):
            NotificationLabel(self.ui, "Password must be at least 6 characters and include both uppercase and lowercase letters.", success=False, duration=3000)
            return
        
        if password != confirm_password:
            NotificationLabel(self.ui, "Confirm password do not match.", success=False, duration=3000)
            return
        
        # find email in database
        with self.ui.db.cursor() as cursor:
            # check email whether has been registed or not
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                NotificationLabel(self.ui, "This email has already been registered. Please take another one.", success=False, duration=3000)
                return
            
            try:
                print(gender)
                cursor.execute("SELECT * FROM users LIMIT 0")
                columns = [desc[0] for desc in cursor.description]
                columns = [col for col in columns if col != 'user_id']
                
                #生成動態的sql程式碼
                placeholders = ', '.join(['%s'] * len(columns))
                columns_sql = ', '.join(columns)

                sql = f"INSERT INTO users ({columns_sql}) VALUES ({placeholders})"
                
                #要新增的元組
                value=(firstname + ' ' + lastname, password, 'icons/non user.png', age, gender, register_time, email)
                
                cursor.execute(sql, value)
                self.db.commit()

                # register success
                NotificationLabel(self.ui, "Registration success.", success=True)
                self.reg_ui.hide()
                self.login_ui.show()
                self.reg_firstname_lineedit.clear()
                self.reg_lastname_lineedit.clear()
                self.reg_age_lineedit.clear()
                self.reg_gender_combobox.setCurrentIndex(0)
                self.reg_mail_lineedit.clear()
                self.reg_password_lineedit.clear()
                self.reg_confirm_password_lineedit.clear()
                self.user_id = cursor.lastrowid
                self.user_id_signal.emit(self.user_id)
                

            except Exception as e:
                print(f"Error during registration: {e}")
                NotificationLabel(self.ui, "Registration failed due to server error.", success=False, duration=3000)
            
    def send_code(self):
        email = self.forgot_mail_linnedit.text()
        if not email:
            NotificationLabel(self.ui, "Email field is required", success=False, duration=3000)

        with self.ui.db.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()

            if not result:
                NotificationLabel(self.ui, "This email is not exist. Please try again.", success=False, duration=3000)
                return

        code = f'{random.randint(0, 999999):06d}'

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.login('gary8321233@gmail.com', 'tsef mthv axiy gxrj')
        from_addr = 'gary8321233@gmail.com'
        to_addr = email
        msg = f'Subject:AI Yoga Coach Verification Code\n{code}'
        status = smtp.sendmail(from_addr, to_addr, msg)
        if status == {}:
            NotificationLabel(self.ui, f"Verification code has been sent out to your email: \n {email}", success=True, duration=3000)
            self.sent_code = code
            self.sent_email = email
        else:
            NotificationLabel(self.ui, f"Fail to sent code.", success=False, duration=3000)

        smtp.quit()
    
    def verify_code(self):
        if (self.forgot_verification_code_lineedit.text() == self.sent_code) and (self.sent_code):
            self.forgot_mail_linnedit.clear()
            self.forgot_verification_code_lineedit.clear()
            self.forgot_ui.hide()
            self.reset_ui.show()
        elif not self.sent_code:
            NotificationLabel(self.ui, f"Fail! Please get verification code first.", success=False, duration=3000)
        else:
            NotificationLabel(self.ui, f"Fail! Please try again.", success=False, duration=3000)
    
    def reset_password(self):
        email = self.sent_email
        password = self.reset_password_lineedit.text()
        confirm_password = self.reset_confirm_password_lineedit.text()

        if not password or not confirm_password:
            NotificationLabel(self.ui, "All fields are required.", success=False, duration=3000)
            return
        
        if not self.is_valid_password(password):
            NotificationLabel(self.ui, "Password must be at least 6 characters and include both uppercase and lowercase letters.", success=False, duration=3000)
            return
        
        if password != confirm_password:
            NotificationLabel(self.ui, "Confirm password do not match.", success=False, duration=3000)
            return
        
        # 更新資料庫密碼
        try:
            with self.ui.db.cursor() as cursor:
                sql = "UPDATE users SET user_password = %s WHERE email = %s"
                cursor.execute(sql, (password, email))
                self.ui.db.commit()

            NotificationLabel(self.ui, "Password has been reset successfully.", success=True)

            # 清除欄位並回到登入畫面
            self.reset_password_lineedit.clear()
            self.reset_confirm_password_lineedit.clear()
            self.reset_ui.hide()
            self.login_ui.show()

        except Exception as e:
            NotificationLabel(self.ui, f"Reset password failed due to server error.", success=False, duration=3000)
        
    def logout(self, delete=False):
        if delete:
            self.camera_btn.setChecked(False)
            self.on_camera_btn_toggled
            self.login_flag = False
            self.user_id = 1
            self.ui.account_status_label.setText("Guest")
            self.ui.stackedWidget.setCurrentIndex(6)
            self.login_ui.show()
            NotificationLabel(self.ui, "Delete success.", success=True, duration=3000)
            return

        if self.login_flag:
            reply = QMessageBox.question(self.ui, "Logout", "Are You sure to logout?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.camera_btn.setChecked(False)
                self.on_camera_btn_toggled
                self.login_flag = False
                self.user_id = 1
                self.ui.account_status_label.setText("Guest")
                self.ui.stackedWidget.setCurrentIndex(6)
                self.login_ui.show()
                NotificationLabel(self.ui, "Logout success.", success=True, duration=3000)
        else:
            self.ui.stackedWidget.setCurrentIndex(6)
        
        
