from PyQt5.QtGui import QPixmap
from notification import NotificationLabel
class User_Info:
    def __init__(self, ui, user_id):
        
        self.ui = ui
        self.db = self.ui.db
        self.user_id= user_id
        self.stackedWidget= self.ui.stackedWidget
        
        #widgets initialization
        self.adjust_password_widget=self.ui.adjust_password_widget
        self.adjust_information_widget=self.ui.adjust_information_widget
        self.user_information_widget=self.ui.user_information_widget
        
        #buttons initialization
        self.config_password=self.ui.config_password
        self.config_user_information=self.ui.config_user_information
        self.data_change_cancel=self.ui.data_change_cancel
        self.change_password_cancel=self.ui.change_password_cancel
        self.password_confirm=self.ui.password_confirm
        self.adjust_confirm=self.ui.adjust_confirm
       
        #user info ui elements initialization
        self.user_name=self.ui.user_name
        self.user_account=self.ui.user_account
        self.user_age=self.ui.user_age
        self.user_gender=self.ui.user_gender
        self.user_register_time=self.ui.user_register_time
        self.user_picture=self.ui.user_picture
        
        #change password ui elements initialization
        self.old_password=self.ui.old_password
        self.new_password=self.ui.new_password
        self.new_password_confirm=self.ui.new_password_confirm
        
        #change user info ui elements initialization
        self.new_name=self.ui.new_name
        self.new_account=self.ui.new_account
        self.new_age=self.ui.new_age
        self.select_genger=self.ui.select_genger
       
        # ui initialization
        self.adjust_password_widget.hide()
        self.adjust_information_widget.hide()
        
        #button event
        self.config_password.clicked.connect(self.change_user_info_widget)
        self.config_user_information.clicked.connect(self.change_user_info_widget)
        self.data_change_cancel.clicked.connect(self.change_user_info_widget)
        self.change_password_cancel.clicked.connect(self.change_user_info_widget)
        self.password_confirm.clicked.connect(self.change_password)
        self.adjust_confirm.clicked.connect(self.change_info)
        
        #user info dict
        self.user_dict=self.get_sql_data()
        
        self.initialize_user_info()
    
    # read sql data
    def get_sql_data(self):
        with self.db.cursor() as cursor:
            sql = "SELECT * FROM users WHERE user_id = %s"
            cursor.execute(sql, (self.user_id,))
            result = cursor.fetchone()
            return result
    
    # initialize/change user info acording to user_id
    def initialize_user_info(self):
        self.user_name.setText(self.user_dict['user_account'])
        self.user_account.setText(self.user_dict['email'])
        self.user_age.setText(str(self.user_dict['age']))
        self.user_gender.setText(self.user_dict['gender'])
        self.user_register_time.setText(str(self.user_dict['register_date']))
        self.user_picture.setPixmap(QPixmap(self.user_dict['user_picture']))  # Assuming profile_picture is a QPixmap or similar
    def set_placeholder(self):
        self.user_dict=self.get_sql_data()
        self.new_name.setText(self.user_dict['user_account'])
        self.new_account.setText(self.user_dict['email'])      
        self.new_age.setText(str(self.user_dict['age']))
        self.select_genger.setCurrentText(self.user_dict['gender'])
    # change user info page widgets
    def change_user_info_widget(self):
        if self.config_password.isChecked():
            self.user_information_widget.hide()
            self.adjust_password_widget.show()
            self.config_password.setChecked(False)
            
        if self.config_user_information.isChecked():
            self.user_information_widget.hide()
            self.adjust_information_widget.show()
            self.config_user_information.setChecked(False)
            self.set_placeholder()
        if self.data_change_cancel.isChecked():
            self.adjust_information_widget.hide()
            self.user_information_widget.show()
            self.data_change_cancel.setChecked(False)
            
        if self.change_password_cancel.isChecked():
            self.adjust_password_widget.hide()
            self.user_information_widget.show()
            self.change_password_cancel.setChecked(False)
    
    # do what when signal received from main.py
    def on_signal_received(self, msg1):
        self.user_id = msg1
        self.user_dict=self.get_sql_data()
        self.initialize_user_info()
    
    # event when change password 
    def change_password(self):
        old_password = self.old_password.text()
        new_password = self.new_password.text()
        new_password_confirm = self.new_password_confirm.text()
        
        if new_password != new_password_confirm:
            NotificationLabel(self.ui, "confirm password unmatch", success=False)
            return
        elif new_password == old_password:
            NotificationLabel(self.ui, "confirm password unmatch", success=False)
            return
        
        self.user_dict=self.get_sql_data()
        with self.db.cursor() as cursor:
            sql = "SELECT user_password FROM users WHERE user_id = %s"
            cursor.execute(sql, (self.user_id,))
            
            if self.user_dict['user_password'] == old_password:
                update_sql = "UPDATE users SET user_password = %s WHERE user_id = %s"
                cursor.execute(update_sql, (new_password, self.user_id))
                self.db.commit()
                NotificationLabel(self.ui, "password update success", success=True)
                self.adjust_password_widget.hide()
                self.user_information_widget.show()
                self.change_password_cancel.setChecked(False)
            else:
                NotificationLabel(self.ui, "old password wrong", success=False)
    
    # event when change user info        
    def change_info(self):
        new_name = self.new_name.text()
        new_account = self.new_account.text()       
        new_age = self.new_age.text()
        select_genger = self.select_genger.currentText()
        if select_genger =="男":
            select_genger="male"
        elif select_genger =="女":
            select_genger="female"
        elif select_genger =="其他":
            select_genger="other"
        self.user_dict=self.get_sql_data()
        with self.db.cursor() as cursor:
            sql = "UPDATE users SET user_account = %s,age = %s,gender = %s,email = %s WHERE user_id = %s"
            cursor.execute(sql, (new_name,new_age,select_genger,new_account,self.user_id))
            self.db.commit()
            self.adjust_information_widget.hide()
            self.user_information_widget.show()
            self.data_change_cancel.setChecked(False)
            self.user_dict=self.get_sql_data()
            self.initialize_user_info()
            NotificationLabel(self.ui, "confirm success", success=True)
            
          
        