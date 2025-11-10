import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import  View, Button
from datetime import datetime

from utils.db import (
    remove_specific_reminder,
    set_user_reminder,
    get_user_reminders,
    remove_user_reminder,
    get_all_reminders,
    remove_outdated_reminders
)

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()
        
    def cog_unload(self):
        self.check_reminders.cancel()    
    
    @tasks.loop(minutes=1)
    async def check_reminders(self):
        try:
            now = datetime.now()
            today = now.date()
            weekday = now.weekday()  # Monday is 0 and Sunday is 6
            async with self.bot.db_lock:
                reminders = await get_all_reminders(self.bot.db)
            for reminder in reminders:
                match_date = reminder['reminder_date'] is None or reminder['reminder_date'] == today
                match_weekday = reminder['weekday'] is None or reminder['weekday'] == weekday
                match_time = reminder['hour'] == now.hour and reminder['minute'] == now.minute
                if match_date and match_weekday and match_time:
                    print("Sending reminder to user:", reminder['discord_id'])
                    user = await self.bot.fetch_user(reminder['discord_id'])
                    if user:
                        try:
                            await user.send(reminder['reminder_string'] if reminder['reminder_string'] is not None else "🧘‍♀️ Time for your Yoga exercise! 🧘‍♂️")
                        except Exception as e:
                            print(f"Failed to send DM reminder to user {reminder['discord_id']}: {e}")
            # Clean up outdated reminders
            async with self.bot.db_lock:
                await remove_outdated_reminders(self.bot.db)
        except Exception as e:
            print("Error in reminder task:", e)
            
    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()
    
    @commands.hybrid_command(
        name="set_reminder",
        description="Set a reminder for your Yoga exercise."
    )
    @app_commands.describe(
        time_str="Time in HH:MM format",
        reminder_type="Type of reminder(daily/weekday/date)",
        value="Optional: weekday number 1–7 or date YYYY-MM-DD",
        reminder_string="Optional: Customize the reminder content\nDefault: <Time for your Yoga exercise!>"
    )
    @app_commands.choices(reminder_type=[
        app_commands.Choice(name="daily", value="daily"),
        app_commands.Choice(name="weekday", value="weekday"),
        app_commands.Choice(name="date", value="date")
    ])
    async def set_reminder(
        self, ctx, time_str: str = None, reminder_type: str = None, value: str = None, reminder_string: str = "🧘‍♀️ Time for your Yoga exercise! 🧘‍♂️"
    ):
        """
        Usage examples:
        /set_reminder 8:30 daily [optional reminder string]       # Daily Notification
        /set_reminder 7:00 weekday 2  [optional reminder string]     # specify weekday as number 1–7 (1=Monday, 7=Sunday).
        /set_reminder 6:45 date 2025-10-31  [optional reminder string]  # specify date as YYYY-MM-DD
        """
        mention = f"<@{ctx.author.id}>"

        if not time_str or ":" not in time_str:
            await ctx.reply("❌ Please specify time in HH:MM format.", ephemeral=True)
            return
        
        hour, minute = map(int, time_str.split(":"))
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            await ctx.reply("❌ Invalid time. Hour must be 0–23 and minute 0–59.", ephemeral=True)
            return
        
        if not reminder_type:
            await ctx.reply("❌ Please specify reminder type: `daily`, `weekday`, or `date`.", ephemeral=True)
        reminder_type = reminder_type.lower()

        if reminder_type == "daily":
            async with self.bot.db_lock:
                await set_user_reminder(self.bot.db, ctx.author.id, hour, minute, None, None, reminder_string)
            msg = f"✅ Daily reminder set at `{hour:02d}:{minute:02d}`"
        elif reminder_type == "weekday":
            if value is None or not value.isdigit() or not (1 <= int(value) <= 7):
                await ctx.reply("❌ Please specify weekday as number 1–7 (1=Monday, 7=Sunday).", ephemeral=True)
                return
            weekday = int(value)
            await set_user_reminder(self.bot.db, ctx.author.id, hour, minute, None, weekday, reminder_string)
            weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            msg = f"✅ Weekly reminder set for every `{weekday_names[weekday - 1]}` at `{hour:02d}:{minute:02d}`\nReminder Content: {reminder_string}"
        elif reminder_type == "date":
            try:
                reminder_date = datetime.strptime(value, "%Y-%m-%d").date()
            except Exception:
                await ctx.reply("❌ Invalid date format. Please use YYYY-MM-DD.", ephemeral=True)
                return
            await set_user_reminder(self.bot.db, ctx.author.id, hour, minute, reminder_date, None, reminder_string)
            msg = f"✅ Reminder set for `{reminder_date}` at `{hour:02d}:{minute:02d}`"
        else:
            await ctx.reply("❌ Invalid type. Use `daily`, `weekday`, or `date`.", ephemeral=True)
            return

        await ctx.reply(f"{mention} {msg}", ephemeral=True)

    @commands.hybrid_command(
        name="remove_all_reminders",
        description="Remove all your reminders"
    )
    async def remove_all_reminders(self, ctx):
        mention = f"<@{ctx.author.id}>"

        view = View(timeout=15)  

        confirm_button = Button(label="✅ Yes, delete all", style=discord.ButtonStyle.red)
        cancel_button = Button(label="❌ Cancel", style=discord.ButtonStyle.gray)

        async def confirm_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("This is not for you.", ephemeral=True)
                return
            try:
                async with self.bot.db_lock:
                    await remove_user_reminder(self.bot.db, ctx.author.id)
                await interaction.response.edit_message(content=f"{mention} ✅ All reminders removed.", view=None)
            except Exception as e:
                await interaction.response.edit_message(content=f"{mention} ❌ Failed to remove reminders.", view=None)
                print("Error in remove_reminder:", e)

        async def cancel_callback(interaction):
            if interaction.user != ctx.author:
                await interaction.response.send_message("This is not for you.", ephemeral=True)
                return
            await interaction.response.edit_message(content=f"{mention} ❌ Cancelled.", view=None)

        confirm_button.callback = confirm_callback
        cancel_button.callback = cancel_callback

        view.add_item(confirm_button)
        view.add_item(cancel_button)

        await ctx.reply(f"{mention} ⚠️ Are you sure you want to delete **all your reminders**?", view=view, ephemeral=True)
    
    @commands.hybrid_command(
        name="list_reminders",
        description="List your reminders and optionally remove specific ones."
    )
    async def list_reminders(self, ctx):
        mention = f"<@{ctx.author.id}>"
        async with self.bot.db_lock:
            reminders = await get_user_reminders(self.bot.db, ctx.author.id)
        if not reminders:
            await ctx.reply(f"{mention} ⚠️ You have no reminders set.", ephemeral=True)
            return

        view = View(timeout=60)

        for r in reminders:
            if r["reminder_date"]:
                text = f"{r['hour']:02d}:{r['minute']:02d} on {r['reminder_date']}"
            elif r["weekday"] is not None:
                text = f"{r['hour']:02d}:{r['minute']:02d} every {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][r['weekday']]}"
            else:
                text = f"{r['hour']:02d}:{r['minute']:02d} daily"

            button = Button(label=f"Delete {text}", style=discord.ButtonStyle.red)

            async def button_callback(interaction, rem=r, btn=button):
                if interaction.user != ctx.author:
                    if not interaction.response.is_done():
                        await interaction.response.send_message("This is not for you.", ephemeral=True)
                    return

                try:
                    async with self.bot.db_lock:
                        await remove_specific_reminder(
                            self.bot.db, ctx.author.id, rem["hour"], rem["minute"], rem["reminder_date"], rem["weekday"]
                        )
                        
                    if not interaction.response.is_done():
                        await interaction.response.send_message(f"✅ Delete selected reminder successfully", ephemeral=True)

                    btn.disabled = True
                    try:
                        await interaction.message.edit(view=view)
                    except discord.NotFound:
                        pass

                except Exception as e:
                    if not interaction.response.is_done():
                        await interaction.response.send_message("❌ Failed to delete reminder.", ephemeral=True)
                    print("Error deleting specific reminder:", e)

            button.callback = button_callback
            view.add_item(button)

        await ctx.reply(
            f"{mention} Here are your reminders:\n⚠️ **Only one reminder record can be deleted at a time**",
            view=view,
            ephemeral=True
        )
