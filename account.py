from PyQt5.QtCore import QObject, pyqtSignal
from datetime import datetime
from notification import NotificationLabel

class Account(QObject):
    user_id_signal = pyqtSignal(int)
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.db = ui.db
        self.stackedWidget= self.ui.stackedWidget
        self.account_status_label = self.ui.account_status_label
        
        # widgets intialization
        self.reg_ui = ui.reg_ui
        self.forgot_ui = ui.forgot_ui
        self.login_ui = ui.login_ui
        
        # buttons initialization
        self.login_register_btn = ui.login_register_btn
        self.login_forgot_btn = ui.login_forgot_btn
        self.reg_back_btn = ui.reg_back_btn
        self.forgot_back_btn = ui.forgot_back_btn
        self.login_btn = ui.login_btn
        
        # ui initialization
        self.reg_ui.hide()
        self.forgot_ui.hide()
        
        #loggin ui elements initialization
        self.login_mail_lineedit=ui.login_mail_lineedit
        self.login_password_lineedit=ui.login_password_lineedit
        
        #register ui elements initialization
        self.reg_register_btn=self.ui.reg_register_btn
        self.reg_firstname_lineedit=self.ui.reg_firstname_lineedit
        self.reg_lastname_lineedit=self.ui.reg_lastname_lineedit
        self.reg_mail_lineedit=self.ui.reg_mail_lineedit
        self.reg_password_lineedit=self.ui.reg_password_lineedit
        self.reg_confirm_password_lineedit=self.ui.reg_confirm_password_lineedit
        
        #button event
        self.login_register_btn.clicked.connect(self.change_account_widget)
        self.login_forgot_btn.clicked.connect(self.change_account_widget)
        self.reg_back_btn.clicked.connect(self.change_account_widget)
        self.forgot_back_btn.clicked.connect(self.change_account_widget)
        self.login_btn.clicked.connect(self.loggin)
        self.reg_register_btn.clicked.connect(self.register)
        
        self.user_id = 1
        self.loggin_flag = False
        
    # change account page widget
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

    # event handler for logging in
    def loggin(self):
        mail = self.login_mail_lineedit.text()
        password = self.login_password_lineedit.text()
        
        # find email in database
        with self.ui.db.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (mail,))
            result = cursor.fetchone()
            
            # has this email
            if result:
                if password == result['user_password']:# check password
                    self.user_id= result['user_id']
                    self.loggin_flag = True
                    NotificationLabel(self.ui, "loggin success", success=True)
                    self.user_id_signal.emit(self.user_id)
                    self.login_mail_lineedit.clear()
                    self.login_password_lineedit.clear()
                    self.stackedWidget.setCurrentIndex(0)
                    self.account_status_label.setText(result['user_account'])
                else:
                    NotificationLabel(self.ui, "wrong password", success=False)
            else:
                NotificationLabel(self.ui, "uninsist email", success=False)
    
    # event handler for registering a new account
    def register(self):
        firstname = self.reg_firstname_lineedit.text()
        lastname = self.reg_lastname_lineedit.text()
        mail = self.reg_mail_lineedit.text()
        password = self.reg_password_lineedit.text()
        confirm_password = self.reg_confirm_password_lineedit.text()
        register_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if password != confirm_password:
            NotificationLabel(self.ui, "confirm password unmatch", success=False)
            return
        
        with self.ui.db.cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM users LIMIT 0")
                columns = [desc[0] for desc in cursor.description]
                columns = [col for col in columns if col != 'user_id']
                #生成動態的sql程式碼
                placeholders = ', '.join(['%s'] * len(columns))
                columns_sql = ', '.join(columns)
                sql = f"INSERT INTO users ({columns_sql}) VALUES ({placeholders})"
                #要新增的元組
                value=(firstname+' '+lastname,password,'icons/non user.png',None,'other',register_time,mail)
                cursor.execute(sql,value)
                self.db.commit()
                NotificationLabel(self.ui, "register success", success=False)
                self.reg_firstname_lineedit.clear()
                self.reg_lastname_lineedit.clear()
                self.reg_mail_lineedit.clear()
                self.reg_password_lineedit.clear()
                self.reg_confirm_password_lineedit.clear()
                self.account_status_label.setText(firstname+' '+lastname)
                self.user_id = cursor.lastrowid
                self.user_id_signal.emit(self.user_id)
                self.stackedWidget.setCurrentIndex(0)
            except Exception as e:
                print(f"Error during registration: {e}")
            
        