import discord
import asyncio
import logging
from discord.ext import commands
from utils.db import connect_db, close_db
from cogs.AccountBinding import AccountBinding
from cogs.Reminder import Reminder
from cogs.GameHanoi import HanoiGame
from cogs.ExportCharts import ExportCharts
from cogs.DMChartSender import DMChartSender
from cogs.LoginNotification import LoginNotification
from config import BOT_TOKEN, COMMAND_PREFIX, ACTIVITY_STATUS, STATUS_TYPE

logging.basicConfig(level=logging.INFO) 

class AIYogaCoachBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)
        self.activity = discord.Activity(type=getattr(discord.ActivityType, STATUS_TYPE), name=ACTIVITY_STATUS)
        self.db = None
        self.db_lock = asyncio.Lock()
        
    async def setup_hook(self):
        self.db = await connect_db()
        await self.add_cog(AccountBinding(self))
        await self.add_cog(Reminder(self))
        await self.add_cog(HanoiGame(self))
        await self.add_cog(ExportCharts(self))
        await self.add_cog(DMChartSender(self))
        await self.add_cog(LoginNotification(self))
        await self.tree.sync()
    
    async def on_ready(self):
        await self.change_presence(activity=self.activity)
        print(f'Logged in as {self.user} (ID: {self.user.id})')
    
    async def close(self):
        await close_db(self.db)
        await super().close()

if __name__ == "__main__":
    bot = AIYogaCoachBot()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.start(BOT_TOKEN))
    except KeyboardInterrupt:
        print("Shutting down...")
        loop.run_until_complete(bot.close())
    finally:
        tasks = asyncio.all_tasks(loop)
        for t in tasks:
            t.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()