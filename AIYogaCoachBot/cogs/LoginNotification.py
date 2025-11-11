import asyncio
from discord.ext import commands, tasks
from datetime import datetime

class LoginNotification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_login_queue.start()
        
    def cog_unload(self):
        self.check_login_queue.cancel()
    
    @tasks.loop(seconds=3)
    async def check_login_queue(self):
        try:
            async with self.bot.db_lock:
                async with self.bot.db.cursor() as cursor:
                    sql = """
                    SELECT discord_id, login_time
                    FROM login_notification_queue
                    WHERE is_notified = FALSE
                    """
                    await cursor.execute(sql)
                    rows = await cursor.fetchall()
        except Exception as e:
            print("DB query error in LoginNotification:", e)
            return
        for row in rows:
            try:
                discord_id = row['discord_id']
                login_time = row['login_time']
                user = await self.bot.fetch_user(discord_id)
                if user is None:
                    continue
                message = f"✅ You have successfully logged in **<AI Yoga Coach App>** on {login_time.strftime('%Y-%m-%d at %H:%M:%S')}."
                # set is_notified to TRUE if successful sent DM to user
                sql = """
                UPDATE login_notification_queue
                SET is_notified = TRUE
                WHERE discord_id = %s AND login_time = %s
                """
                async with self.bot.db_lock:
                    async with self.bot.db.cursor() as cursor:
                        await cursor.execute(sql, (discord_id, login_time.strftime("%Y-%m-%d %H:%M:%S")))
                    await self.bot.db.commit()
                try:
                    await user.send(message)
                except Exception as e:
                    print("Error sending login notification DM in LoginNotification:", e)
            except Exception as e:
                print("Error processing login notification in LoginNotification:", e)
            await asyncio.sleep(1)  # To avoid hitting rate limits
    
    @check_login_queue.before_loop
    async def before_check_login_queue(self):
        await self.bot.wait_until_ready()