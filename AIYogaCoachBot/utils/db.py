import asyncio
from datetime import datetime
import aiomysql
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT
import hashlib
from datetime import date

async def connect_db():
    try:
        db = await aiomysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            port=DB_PORT,
            cursorclass=aiomysql.cursors.DictCursor
        )
        print("aiomysql connected successfully")
        return db
    except Exception as e:
        print("aiomysql connection error: ", e)
        return None


async def close_db(db):
    if db:
        db.close()
        print("aiomysql connection closed")



async def get_user_id(db, user_email: str, user_password: str) -> int:
    if not db:
        return -1

    password_hash = hashlib.sha256(user_password.encode('utf-8')).hexdigest()
    try:
        async with db.cursor() as cursor:
            print(f'Querying user_id for account: {user_email} with hashed password: {password_hash}')
            sql = """
            SELECT user_id 
            FROM users 
            WHERE email = %s AND user_password = %s
            """
            await cursor.execute(sql, (user_email, password_hash))
            result = await cursor.fetchone()
            return result['user_id'] if result else -1
    except Exception as e:
        print("DB query error:", e)
        return -1

async def get_user_id_by_discord_id(db, discord_id: int) -> int:
    if not db:
        return -1
    
    try:
        async with db.cursor() as cursor:
            sql = """
            SELECT user_id 
            FROM discord_users 
            WHERE discord_id = %s
            """
            await cursor.execute(sql, (discord_id,))
            result = await cursor.fetchone()
            return result['user_id'] if result else -1
    except Exception as e:
        print("DB query error:", e)
        return -1

async def get_user_info(db, user_id: int) -> dict:
    if not db:
        return {}
    
    try:
        async with db.cursor() as cursor:
            sql = """
            SELECT *
            FROM users
            WHERE user_id = %s
            """
            await cursor.execute(sql, (user_id,))
            result = await cursor.fetchone()
            return result if result else {}
    except Exception as e:
        print("DB query error:", e)
        return {}


async def bind_discord_user(db, discord_id: int, user_id: int) -> bool:
    if not db:
        return False

    try:
        async with db.cursor() as cursor:
            sql = """
            INSERT INTO discord_users (discord_id, user_id, bind_date)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                user_id = %s,
                bind_date = %s
            """
            now = datetime.now()
            await cursor.execute(sql, (discord_id, user_id, now, user_id, now))
        await db.commit()
        print(f'Discord user {discord_id} bound to user {user_id} successfully.')
        return True
    except Exception as e:
        print("DB bind error:", e)
        await db.rollback()
        return False
    
    
async def unbind_discord_user(db, discord_id: int) -> bool:
    if not db:
        return False

    try:
        async with db.cursor() as cursor:
            sql = "DELETE FROM discord_users WHERE discord_id = %s"
            await cursor.execute(sql, (discord_id,))
        await db.commit()
        print(f'Discord user {discord_id} unbound successfully.')
        return True
    except Exception as e:
        print("DB unbind error:", e)
        await db.rollback()
        return False


async def set_user_reminder(db, discord_id: int, hour: int, minute: int, reminder_date=None, weekday=None, reminder_string=None) -> bool:
    if not db:
        return False
    
    try:
        async with db.cursor() as cursor:
            sql = """
            INSERT INTO reminders (discord_id, hour, minute, reminder_date, weekday, reminder_string)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                reminder_date = VALUES(reminder_date),
                weekday = VALUES(weekday)
            """
            await cursor.execute(sql, (discord_id, hour, minute, reminder_date, (weekday - 1 if weekday is not None else None), reminder_string))
        await db.commit()
        print(f'Reminder set for Discord user {discord_id} at {hour}:{minute}.')
        return True
    except Exception as e:
        print("DB set reminder error:", e)
        await db.rollback()
        return False


async def get_user_reminders(db, discord_id: int) -> list:
    if not db:
        return []
    
    try:
        async with db.cursor() as cursor:
            print(discord_id)
            sql = "SELECT discord_id, hour, minute, reminder_date, weekday FROM reminders WHERE discord_id = %s"
            await cursor.execute(sql, (discord_id,))
            results = await cursor.fetchall()
        return results
    except Exception as e:
        print("DB get reminder error:", e)
        return []


async def get_all_reminders(db) -> list:
    if not db:
        return []
    
    try:
        async with db.cursor() as cursor:
            sql = "SELECT discord_id, hour, minute, reminder_date, weekday, reminder_string FROM reminders"
            await cursor.execute(sql)
            results = await cursor.fetchall()
        return results
    except Exception as e:
        print("DB get all reminders error:", e)
        return []


async def remove_user_reminder(db, discord_id: int, hour=None, minute=None) -> bool:
    if not db:
        return False
    
    try:
        async with db.cursor() as cursor:
            if hour is not None and minute is not None:
                sql = "DELETE FROM reminders WHERE discord_id = %s AND hour = %s AND minute = %s"
                await cursor.execute(sql, (discord_id, hour, minute))
            else:
                sql = "DELETE FROM reminders WHERE discord_id = %s"
                await cursor.execute(sql, (discord_id,))
        await db.commit()
        print(f'Reminder(s) removed for Discord user {discord_id}.')
        return True
    except Exception as e:
        print("DB remove reminder error:", e)
        await db.rollback()
        return False


async def remove_specific_reminder(db, discord_id: int, hour: int, minute: int, reminder_date=None, weekday=None) -> bool:
    if not db:
        return False

    try:
        async with db.cursor() as cursor:
            sql = """
            DELETE FROM reminders
            WHERE discord_id=%s AND hour=%s AND minute=%s
            AND ((reminder_date IS NULL AND %s IS NULL) OR reminder_date=%s)
            AND ((weekday IS NULL AND %s IS NULL) OR weekday=%s)
            """
            await cursor.execute(sql, (discord_id, hour, minute, reminder_date, reminder_date, weekday, weekday))
        await db.commit()
        return True
    except Exception as e:
        print("DB remove_specific_reminder error:", e)
        return False


async def remove_outdated_reminders(db) -> bool:
    if not db:
        return False
    
    try:
        now = datetime.now()
        
        async with db.cursor() as cursor:
            sql = """
            DELETE FROM reminders
            WHERE reminder_date IS NOT NULL
            AND TIMESTAMP(reminder_date, CONCAT(LPAD(hour,2,'0'), ':', LPAD(minute,2,'0'))) < %s
            """
            await cursor.execute(sql, (now,))
        await db.commit()
        return True
    except Exception as e:
        print("DB remove outdated reminders error:", e)
        await db.rollback()
        return False

if __name__ == "__main__":
    async def test():
        db = await connect_db()
        await close_db(db)
    asyncio.run(test())
    
