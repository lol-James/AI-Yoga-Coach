import os
import shutil
import pymysql
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import *
from PyQt5 import uic
from datetime import datetime
from functools import partial
from notification import NotificationLabel

scrollbar_style = """
    QScrollBar:vertical {
        border: none;
        background: transparent;
        width: 8px;
        margin: 0px;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical {
        background-color: rgba(0, 0, 0, 80);
        min-height: 20px;
        border-radius: 4px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: rgba(0, 0, 0, 120);
    }

    QScrollBar::handle:vertical:pressed {
        background-color: rgba(0, 0, 0, 160);
    }

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {
        height: 0px;
        background: none;
    }

    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        background: none;
    }
    """

class PostDialog:
    def __init__(self, ui, user_id, db_conn):
        
        self.ui = ui
        self.user_id = user_id
        self.db_conn = db_conn
        self.selected_image_path = None
        self.ui.scrollArea.verticalScrollBar().setStyleSheet(scrollbar_style)
        self.ui.scrollArea_2.verticalScrollBar().setStyleSheet(scrollbar_style)

        self.ui.link_button.clicked.connect(self.select_image)
        self.ui.pushButton_10.clicked.connect(self.submit_post)

        self.ui.refresh_btn.clicked.connect(self.refresh_posts)

        self.ui.label_5.setAlignment(Qt.AlignCenter)
        self.ui.label_5.setText("請點擊左側按鈕選擇圖片")

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
            NotificationLabel(self.ui, "❌ 請輸入文字或選擇圖片", success=False)
            return

        share_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        image_data = None
        if self.selected_image_path:
            try:
                with open(self.selected_image_path, "rb") as f:
                    image_data = f.read()  
            except Exception as e:
                NotificationLabel(self.ui, f"❌ 無法讀取圖片：{e}", success=False)
                return

        try:
            with self.db_conn.cursor() as cursor:
                sql = """
                    INSERT INTO share_page (user_id, share_date, share_text, share_content, share_like)
                    VALUES (%s, %s, %s, %s, 0)
                """
                cursor.execute(sql, (self.user_id, share_date, text, image_data))
                self.db_conn.commit()

            NotificationLabel(self.ui, "✅ 貼文已成功發送", success=True)

            self.ui.textEdit_2.clear()
            self.ui.label_5.clear()
            self.ui.label_5.setText("請點擊左側按鈕選擇圖片")
            self.selected_image_path = None

            self.load_posts()
            self.ui.scrollArea.verticalScrollBar().setValue(0)

        except Exception as e:
            NotificationLabel(self.ui, f"❌ 資料庫錯誤：{e}", success=False)


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

        image_data = post.get("share_content")

        if image_data:
            pixmap = QPixmap()
            if isinstance(image_data, (bytes, bytearray)):  
                pixmap.loadFromData(image_data)
            elif isinstance(image_data, str) and os.path.exists(image_data): 
                pixmap.load(image_data)
            else:
                pixmap = QPixmap()  

            if isinstance(pixmap, QPixmap) and not pixmap.isNull():
                scaled_pixmap = pixmap.scaledToWidth(300, Qt.SmoothTransformation)
                frame.put_picture.setPixmap(scaled_pixmap)
                frame.put_picture.setVisible(True)
            else:
                frame.put_picture.clear()
                frame.put_picture.setVisible(False)

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

            available_width = self.ui.scrollArea.width() - 60  

            for post in posts:
                frame = self.create_share_frame(post)

                image_data = post["share_content"]
                if image_data:
                    pixmap = QPixmap()
                    if isinstance(image_data, (bytes, bytearray)): 
                        pixmap.loadFromData(image_data)
                    elif isinstance(image_data, str) and os.path.exists(image_data):  
                        pixmap = QPixmap(image_data)
                    else:
                        pixmap = QPixmap()

                    scaled_pixmap = pixmap.scaledToWidth(
                        available_width,
                        Qt.SmoothTransformation
                    )

                    frame.put_picture.setPixmap(scaled_pixmap)
                    frame.put_picture.setScaledContents(False)
                    frame.put_picture.setAlignment(Qt.AlignCenter)
                    frame.put_picture.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
                    frame.put_picture.adjustSize()

                else:
                    frame.put_picture.clear()

                layout.addWidget(frame)

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

    def reset_post_fields(self):
        if hasattr(self, "selected_image_path") and self.selected_image_path:
            if os.path.exists(self.selected_image_path):
                try:
                    os.remove(self.selected_image_path)
                    print(f"Deleted image: {self.selected_image_path}")
                except Exception as e:
                    print(f"Failed to delete image: {e}")
        self.selected_image_path = None
        self.ui.label_5.clear()
        self.ui.label_5.setText("點擊左側按鈕選擇圖片")
        self.ui.textEdit_2.clear()
    
    def refresh_posts(self):
        try:
            self.db_conn.ping(reconnect=True)
            self.db_conn.commit()

            self.load_posts()
            NotificationLabel(self.ui, "Posts refreshed", success=True)
        except Exception as e:
            NotificationLabel(self.ui, f"Failed to refresh posts：{e}", success=False)  