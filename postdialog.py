import os
import shutil
import pymysql
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import uic
from datetime import datetime
from functools import partial

class PostDialog:
    def __init__(self, ui, user_id, db_conn):
        self.ui = ui
        self.user_id = user_id
        self.db_conn = db_conn
        self.selected_image_path = None

        self.ui.link_button.clicked.connect(self.select_image)
        self.ui.pushButton_10.clicked.connect(self.submit_post)

        self.ui.label_5.setAlignment(Qt.AlignCenter)
        self.ui.label_5.setText("請點擊左側附加檔案選擇圖片")

        self.current_comment_post_id = None  
        self.comment_layout = self.ui.scrollArea_2.findChild(QVBoxLayout, "verticalLayout_25")
        self.share_comment_frame = self.ui.share_comment_frame

        self.ui.send_comment_btn.clicked.connect(self.submit_comment)
        self.comment_target_post_id = None  


    def select_image(self):
        filename, _ = QFileDialog.getOpenFileName(
            None, "選擇圖片", "", "Images (*.png *.jpg *.jpeg)"
        )
        if filename:
            pixmap = QPixmap(filename).scaled(
                self.ui.label_5.width(), self.ui.label_5.height(), Qt.KeepAspectRatio
            )
            self.ui.label_5.setPixmap(pixmap)
            self.selected_image_path = filename

    def submit_post(self):
        text = self.ui.textEdit_2.toPlainText().strip()

        if not text and not self.selected_image_path:
            QMessageBox.warning(None, "錯誤", "請輸入文字或選擇圖片")
            return

        share_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_path_in_db = None

        if self.selected_image_path:
            save_dir = "post_images"
            os.makedirs(save_dir, exist_ok=True)
            filename = os.path.basename(self.selected_image_path)
            dest_path = os.path.join(save_dir, filename)
            try:
                shutil.copy(self.selected_image_path, dest_path)
                image_path_in_db = dest_path
            except Exception as e:
                QMessageBox.warning(None, "圖片儲存錯誤", str(e))
                return

        try:
            with self.db_conn.cursor() as cursor:
                sql = "INSERT INTO share_page (user_id, share_date, share_text, share_content, share_like) VALUES (%s, %s, %s, %s, 0)"
                cursor.execute(sql, (self.user_id, share_date, text, image_path_in_db))
                self.db_conn.commit()

            QMessageBox.information(None, "成功", "貼文已發送")
            print("發送貼文的 user_id：", self.user_id)
            self.ui.textEdit_2.clear()
            self.ui.label_5.clear()
            self.ui.label_5.setText("請點擊左側附加檔案選擇圖片")
            self.selected_image_path = None
            self.load_posts()
            self.ui.scrollArea.verticalScrollBar().setValue(0)

        except Exception as e:
            QMessageBox.critical(None, "資料庫錯誤", str(e))

    def create_share_frame(self, post):
        frame = uic.loadUi("share_frame.ui")

        frame.share_time.setText(str(post['share_date']))
        frame.share_user_name.setText(post['user_account'])
        frame.likeCount.setText(str(post['share_like']))

        if post['user_picture'] and os.path.exists(post['user_picture']):
            icon = QPixmap(post['user_picture']).scaled(
                frame.share_user_icon.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            frame.share_user_icon.setPixmap(icon)
        else:
            frame.share_user_icon.clear()

        if post['share_text']:
            frame.put_word.setText(post['share_text'])         
            frame.put_word.setWordWrap(True)                  
            frame.put_word.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred) 
            frame.put_word.setTextInteractionFlags(Qt.TextSelectableByMouse)  

        else:
            frame.put_word.clear()
            frame.put_word.setVisible(False)

        if post['share_content'] and os.path.exists(post['share_content']):
            pixmap = QPixmap(post['share_content']).scaledToWidth(300, Qt.SmoothTransformation)
            frame.put_picture.setPixmap(pixmap)
            frame.put_picture.setVisible(True)
        else:
            frame.put_picture.clear()
            frame.put_picture.setVisible(False)

        post_id = post['id']
        frame.share_like_btn.clicked.connect(lambda _, pid=post_id, label=frame.likeCount: self.handle_like(pid, label))

        frame.share_comment_btn.clicked.connect(lambda _, pid=post_id: self.toggle_share_comment_widget(pid))

        return frame

    def load_posts(self):
        try:
            cursor = self.db_conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT s.*, u.user_account, u.user_picture 
                FROM share_page s
                JOIN users u ON s.user_id = u.user_id
                ORDER BY s.id DESC
            """)
            posts = cursor.fetchall()

            layout = self.ui.verticalLayout_47
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            for post in posts:
                frame = self.create_share_frame(post)
                self.ui.verticalLayout_47.addWidget(frame)

        except pymysql.MySQLError as e:
            QMessageBox.critical(None, "載入貼文失敗", str(e))

    def handle_like(self, post_id, like_label):
        try:
            with self.db_conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM post_like WHERE post_id = %s AND user_id = %s", (post_id, self.user_id))
                like_record = cursor.fetchone()

                if like_record:
                    cursor.execute("DELETE FROM post_like WHERE post_id = %s AND user_id = %s", (post_id, self.user_id))
                    cursor.execute("UPDATE share_page SET share_like = share_like - 1 WHERE id = %s", (post_id,))
                else:
                    cursor.execute("INSERT INTO post_like (post_id, user_id) VALUES (%s, %s)", (post_id, self.user_id))
                    cursor.execute("UPDATE share_page SET share_like = share_like + 1 WHERE id = %s", (post_id,))

                self.db_conn.commit()

                cursor.execute("SELECT share_like FROM share_page WHERE id = %s", (post_id,))
                result = cursor.fetchone()
                if result:
                    like_label.setText(str(result['share_like']))

        except Exception as e:
            QMessageBox.critical(None, "按讚失敗", str(e))

    def toggle_share_comment_widget(self, post_id):
        if self.share_comment_frame.isVisible() and self.comment_target_post_id == post_id:
            self.share_comment_frame.setVisible(False)
            self.comment_target_post_id = None
        else:
            self.share_comment_frame.setVisible(True)
            self.comment_target_post_id = post_id
            self.load_comments(post_id)






    def load_comments(self, post_id):
        try:
            layout = self.comment_layout
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            cursor = self.db_conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT c.*, u.user_account, u.user_picture 
                FROM comment_page c
                JOIN users u ON c.comment_user_id = u.user_id
                WHERE c.post_id = %s
                ORDER BY c.id DESC
            """, (post_id,))
            comments = cursor.fetchall()

            for comment in comments:
                comment_frame = uic.loadUi("comment_frame.ui")

                comment_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                comment_frame.setMaximumWidth(self.ui.scrollArea_2.viewport().width())

                comment_frame.comment_name_5.setText(comment['user_account'])
                comment_frame.comment_time_5.setText(str(comment['comment_date']))
                comment_frame.comment_text_5.setWordWrap(True)
                comment_frame.comment_text_5.setText(comment['comment_text'])
                comment_frame.like_number_5.setText(str(comment['comment_like']))
                comment_frame.dislike_number_5.setText(str(comment['comment_dislike']))

                if comment['user_picture'] and os.path.exists(comment['user_picture']):
                    pixmap = QPixmap(comment['user_picture']).scaled(
                        comment_frame.user_comment_icon_5.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    comment_frame.user_comment_icon_5.setPixmap(pixmap)
                else:
                    comment_frame.user_comment_icon_5.clear()

                comment_id = comment['id']
                comment_frame.like_button_5.clicked.connect(
                    partial(self.like_comment, comment['id'], comment_frame.like_number_5)
                )
                comment_frame.dislike_button_5.clicked.connect(
                    partial(self.dislike_comment, comment['id'], comment_frame.dislike_number_5)
                )

                layout.addWidget(comment_frame)

        except Exception as e:
            QMessageBox.critical(None, "載入留言失敗", str(e))


        
    def submit_comment(self):
        comment_text = self.ui.comment_input.toPlainText().strip() 

        if not comment_text:
            QMessageBox.warning(None, "提醒", "請輸入留言內容")
            return

        if self.comment_target_post_id is None:
            QMessageBox.warning(None, "錯誤", "無有效貼文可留言")
            return

        try:
            comment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with self.db_conn.cursor() as cursor:
                sql = """
                    INSERT INTO comment_page (post_id, comment_user_id, comment_date, comment_text, comment_like, comment_dislike)
                    VALUES (%s, %s, %s, %s, 0, 0)
                """
                cursor.execute(sql, (self.comment_target_post_id, self.user_id, comment_date, comment_text))
                self.db_conn.commit()

            self.ui.comment_input.clear()
            self.load_comments(self.comment_target_post_id)

        except Exception as e:
            QMessageBox.critical(None, "留言失敗", str(e))

    def like_comment(self, comment_id, label):
        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute("SELECT * FROM comment_like WHERE comment_id = %s AND user_id = %s", (comment_id, self.user_id))
                result = cursor.fetchone()

                if result:
                    cursor.execute("DELETE FROM comment_like WHERE comment_id = %s AND user_id = %s", (comment_id, self.user_id))
                    cursor.execute("UPDATE comment_page SET comment_like = comment_like - 1 WHERE id = %s", (comment_id,))
                else:
                    cursor.execute("INSERT INTO comment_like (comment_id, user_id) VALUES (%s, %s)", (comment_id, self.user_id))
                    cursor.execute("UPDATE comment_page SET comment_like = comment_like + 1 WHERE id = %s", (comment_id,))

                self.db_conn.commit()

                cursor.execute("SELECT comment_like FROM comment_page WHERE id = %s", (comment_id,))
                result = cursor.fetchone()
                if result:
                    label.setText(str(result['comment_like']))
        except Exception as e:
            QMessageBox.critical(None, "留言按讚失敗", str(e))

    def dislike_comment(self, comment_id, label):
        try:
            with self.db_conn.cursor() as cursor:
                cursor.execute("SELECT * FROM comment_dislike WHERE comment_id = %s AND user_id = %s", (comment_id, self.user_id))
                result = cursor.fetchone()

                if result:
                    cursor.execute("DELETE FROM comment_dislike WHERE comment_id = %s AND user_id = %s", (comment_id, self.user_id))
                    cursor.execute("UPDATE comment_page SET comment_dislike = comment_dislike - 1 WHERE id = %s", (comment_id,))
                else:
                    cursor.execute("INSERT INTO comment_dislike (comment_id, user_id) VALUES (%s, %s)", (comment_id, self.user_id))
                    cursor.execute("UPDATE comment_page SET comment_dislike = comment_dislike + 1 WHERE id = %s", (comment_id,))

                self.db_conn.commit()

                cursor.execute("SELECT comment_dislike FROM comment_page WHERE id = %s", (comment_id,))
                result = cursor.fetchone()
                if result:
                    label.setText(str(result['comment_dislike']))
        except Exception as e:
            QMessageBox.critical(None, "留言倒讚失敗", str(e))


    def update_user_id(self, new_user_id):
        self.user_id = new_user_id
        print("PostDialog updated user_id:", self.user_id)