import pymysql
#連線資料庫
def connect_db():
    try:
        db = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='root123456',
            database='yoga_coach_database',
            port=3306,
            connect_timeout=5,
            cursorclass=pymysql.cursors.DictCursor
        )
        print(" pymysql 成功連線！")
        return db
    except Exception as e:
        print(" pymysql 錯誤：", e)


#--------------讀取資料--------------------------------------
def read_db(db):
    with db.cursor() as cursor:
        sql = "SELECT * FROM users WHERE user_account = %s"
        cursor.execute(sql, ('David_Sun',))
        result = cursor.fetchone()
        print(result)
#-----------------------------------------------------------
    
# #--------------新增資料--------------------------------------
def add_db(db):
    with db.cursor() as cursor:
        #先找出table上所有欄位名稱，再排除primary key
        cursor.execute("SELECT * FROM users LIMIT 0")
        columns = [desc[0] for desc in cursor.description]
        columns = [col for col in columns if col != 'user_id']
        #生成動態的sql程式碼
        placeholders = ', '.join(['%s'] * len(columns))
        columns_sql = ', '.join(columns)
        sql = f"INSERT INTO users ({columns_sql}) VALUES ({placeholders})"
        #要新增的元組
        value=('non','00000000','/icon/non_user.png',None,None,None,'deafult')
        cursor.execute(sql,value)
        db.commit()
        print("新增成功")
# #-----------------------------------------------------------

#--------------刪除資料--------------------------------------
def delete_db(db):
    with db.cursor() as cursor:
        sql = "DELETE FROM users WHERE user_account = %s"
        cursor.execute(sql, ('non',))
        db.commit()
        print("刪除成功")
#-----------------------------------------------------------

# #--------------修改資料--------------------------------------
def update_db(db):
    with db.cursor() as cursor:
        sql = "UPDATE users SET user_account = %s WHERE user_id = %s"
        cursor.execute(sql, ('non', 8))
        db.commit()
        print("修改成功")
# #-----------------------------------------------------------
if __name__ == "__main__":
    db = connect_db()

