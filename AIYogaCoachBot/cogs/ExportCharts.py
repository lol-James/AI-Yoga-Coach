import discord
from discord import app_commands
from discord.ext import commands
from datetime import date, datetime
from utils.db import get_user_id_by_discord_id

from utils.generate_chart import fetch_and_group_data, save_group_charts

class ExportCharts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.hybrid_command(
        name="exportcharts",
        description="Export posture accuracy charts as images."
    )
    @app_commands.describe(
        posture="Pose Name (e.g., 'Warrior 1 Pose')",
        mode="Exercise Mode PRACTICE/EASY/HARD",
        start_date="Start Date (YYYY-MM-DD)",
        end_date="End Date (YYYY-MM-DD)"
    )
    @app_commands.choices(
        posture=[
            app_commands.Choice(name="Bridge Pose", value="Bridge Pose"),
            app_commands.Choice(name="Chair Pose", value="Chair Pose"),
            app_commands.Choice(name="Downward-Facing Dog", value="Downward-Facing Dog"),
            app_commands.Choice(name="Locust Pose", value="Locust Pose"),
            app_commands.Choice(name="Plank Pose", value="Plank Pose"),
            app_commands.Choice(name="Staff Pose", value="Staff Pose"),
            app_commands.Choice(name="Triangle Pose", value="Triangle Pose"),
            app_commands.Choice(name="Warrior 1 Pose", value="Warrior 1 Pose"),
            app_commands.Choice(name="Warrior 2 Pose", value="Warrior 2 Pose"),
            app_commands.Choice(name="Warrior 3 Pose", value="Warrior 3 Pose")
        ]
    )
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="PRACTICE", value="PRACTICE"),
            app_commands.Choice(name="EASY", value="EASY"),
            app_commands.Choice(name="HARD", value="HARD")
        ]
    )
    async def export_charts_command(
        self, 
        ctx, 
        posture: str, 
        mode: str, 
        start_date: str = date.today().strftime("%Y-%m-%d"), 
        end_date: str = date.today().strftime("%Y-%m-%d")
    ):
        mention = f"<@{ctx.author.id}>"
        async with self.bot.db_lock:
            user_id = await get_user_id_by_discord_id(self.bot.db, ctx.author.id)
        if user_id == -1:
            await ctx.reply(f"❌ {mention} You need to bind your account first using /bind_account.", ephemeral=True)
            return
        
        if posture.lower() not in [
            "bridge pose", "chair pose", "downward-facing dog", "locust pose",
            "plank pose", "staff pose", "triangle pose",
            "warrior 1 pose", "warrior 2 pose", "warrior 3 pose"
        ]:
            await ctx.reply(f"❌ {mention} Invalid posture name.", ephemeral=True)
            return
        
        mode = mode.upper()
        if mode not in ["PRACTICE", "EASY", "HARD"]:
            await ctx.reply(f"❌ {mention} Invalid mode. Choose from PRACTICE, EASY, HARD.", ephemeral=True)
            return
        
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            await ctx.reply(f"❌ {mention} Invalid date format. Please use YYYY-MM-DD.", ephemeral=True)
            return
        if start_dt > end_dt:
            await ctx.reply(f"❌ {mention} Start date cannot be after end date.", ephemeral=True)
            return
        await ctx.reply(f"⏳ {mention} Generating charts, please wait...", ephemeral=True)
        
        async with self.bot.db_lock:
            data = await fetch_and_group_data(user_id, mode, posture, self.bot.db, start_dt, end_dt)
        
        if not data:
            if isinstance(ctx, discord.Interaction):
                await ctx.followup.send(f"❌ {mention} No data found for the specified criteria.", ephemeral=True)
                return
            else:
                await ctx.reply(f"❌ {mention} No data found for the specified criteria.", ephemeral=True)
                return
        chart_files = await save_group_charts(data, user_id, mode, posture)
        if not chart_files:
            if isinstance(ctx, discord.Interaction):
                await ctx.followup.send(f"❌ {mention} Failed to generate charts.", ephemeral=True)
                return
            else:
                await ctx.reply(f"❌ {mention} Failed to generate charts.", ephemeral=True)
                return
        files = [discord.File(fp) for fp in chart_files]
        if isinstance(ctx, discord.Interaction):
            await ctx.followup.send(f"✅ {mention} Here are your exported charts:", files=files, ephemeral=True)
        else:
            await ctx.reply(
                f"✅ {mention} Here are your exported charts:\n"
                f"Yoga Pose: {posture}\tMode: {mode}\tStart Date: {start_date}\tEnd Date: {end_date}"
                , files=files, ephemeral=True)
        
        