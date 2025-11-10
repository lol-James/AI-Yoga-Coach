import asyncio
import discord
from discord.ext import commands, tasks
from datetime import datetime
from utils.db import get_user_id_by_discord_id

from utils.generate_chart import fetch_and_group_data, save_group_charts

class DMChartSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_bot_message_queue.start()
            
    def cog_unload(self):
        self.check_bot_message_queue.cancel()
    
    @tasks.loop(seconds=5)    
    async def check_bot_message_queue(self):
        try:
            async with self.bot.db_lock:
                async with self.bot.db.cursor() as cursor:
                    sql = """
                    SELECT discord_id, posture, mode, start_date, end_date
                    FROM bot_message_queue
                    WHERE is_received = FALSE
                    """
                    await cursor.execute(sql)
                    rows = await cursor.fetchall()
        except Exception as e:
            print("DB query error in DMChartSender:", e)
            return
        for row in rows:
            try:
                discord_id = row['discord_id']
                posture = row['posture']
                mode = row['mode']
                start_date = datetime.strptime(row['start_date'], "%Y-%m-%d").date()
                end_date = datetime.strptime(row['end_date'], "%Y-%m-%d").date()
                user = await self.bot.fetch_user(discord_id)
                if user is None:
                    continue
                async with self.bot.db_lock:
                    user_id = await get_user_id_by_discord_id(self.bot.db, discord_id)
                if user_id == -1:
                    continue
                async with self.bot.db_lock:
                    data = await fetch_and_group_data(
                        user_id, 
                        mode, 
                        posture, 
                        self.bot.db, 
                        start_date, 
                        end_date
                    )
                if not data:
                    try:
                        await user.send(f"❌ No data found for posture '{posture}' in mode '{mode}' from {start_date} to {end_date}.")
                        continue
                    except Exception as e:
                        print("Error sending no data DM in DMChartSender:", e)
                        continue
                else:
                    async with self.bot.db_lock:
                        chart_files = await save_group_charts(data, user_id, mode, posture)
                if not chart_files:
                    try:
                        await user.send(f"❌ Failed to generate charts for posture '{posture}' in mode '{mode}'.")
                        continue
                    except Exception as e:
                        print("Error sending failed chart DM in DMChartSender:", e)
                        continue
                files = [discord.File(fp) for fp in chart_files]
                try:
                    await user.send(
                        content=f"📊 Here are your charts for posture '{posture}' in mode '{mode}' from {start_date} to {end_date}:",
                        files=files
                    )
                except Exception as e:
                    print("Error sending charts DM in DMChartSender:", e)
                    continue
                async with self.bot.db_lock:
                    async with self.bot.db.cursor() as cursor:
                        update_sql = """
                        UPDATE bot_message_queue
                        SET is_received = TRUE
                        WHERE discord_id = %s AND posture = %s AND mode = %s AND start_date = %s AND end_date = %s
                        """
                        await cursor.execute(update_sql, (discord_id, posture, mode, row['start_date'], row['end_date']))
                        await self.bot.db.commit()
                
                await asyncio.sleep(2)
            except Exception as e:
                print("Error sending DM in DMChartSender:", e)
                continue
            
    @check_bot_message_queue.before_loop
    async def before_check_bot_message_queue(self):
        await self.bot.wait_until_ready()