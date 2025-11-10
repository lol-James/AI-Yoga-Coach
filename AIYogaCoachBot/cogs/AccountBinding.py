import discord
from discord.ext import commands
from discord.ui import View, Button
from utils.db import get_user_id, bind_discord_user, get_user_info, unbind_discord_user

class AccountBinding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(
            name="bind", 
            description="Bind your Discord account to your AI Yoga Coach account."
    )
    async def bind_account(self, ctx, email: str, password: str):
        mention = f"<@{ctx.author.id}>"
        try:
            await ctx.reply(
                f'{mention} Checking your email and password, please wait...\n'
                f'-# The account password you entered has been automatically deleted to ensure security', ephemeral=True)
            async with self.bot.db_lock:
                user_id = await get_user_id(self.bot.db, email, password)
            if user_id == -1:
                await ctx.reply(
                    f"{mention} ❌ **Invalid email or password.**\nPlease check your credentials and try again.", ephemeral=True)
                return
            
            async with self.bot.db_lock:
                success = await bind_discord_user(self.bot.db, ctx.author.id, user_id)
            if success:
                async with self.bot.db_lock:
                    self.user_info = await get_user_info(self.bot.db, user_id)
                await ctx.reply(
                    f"{mention} ✅ **Successfully bound your Discord account to your AI Yoga Coach account!**\n"
                    f"**Username:** `{self.user_info['user_account']}`\n", ephemeral=True)
            else:
                await ctx.reply(
                    f"{mention} ⚠️ **Failed to bind account.** Please try again later.", ephemeral=True)
        except Exception as e:
            await ctx.reply(
                f"{mention} ❌ **An error occurred while processing your request.**", ephemeral=True)
            print("Error in bind_account command:", e)


    @commands.hybrid_command(
        name="unbind",
        description="Unbind your Discord account from your AI Yoga Coach account."
    )
    async def unbind_account(self, ctx):
        mention = f"<@{ctx.author.id}>"
        
        try:
            view = View(timeout=10)  
            result = {"done": False, "success": False} 
            
            confirm_btn = Button(label="Confirm ⭕", style=discord.ButtonStyle.green)
            cancel_btn = Button(label="Cancel ❌", style=discord.ButtonStyle.red)
            view.add_item(confirm_btn)
            view.add_item(cancel_btn)

            async def button_callback(interaction: discord.Interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message("This button is not for you.", ephemeral=True)
                    return
                if interaction.data["custom_id"] == confirm_btn.custom_id:
                    async with self.bot.db_lock:
                        success = await unbind_discord_user(self.bot.db, ctx.author.id)
                    result["done"] = True
                    result["success"] = success
                    reply_text = f"{mention} ✅ **Successfully unbound your Discord account!**" if success else f"{mention} ⚠️ **Failed to unbind account. Please try again later.**"
                else:
                    result["done"] = True
                    reply_text = f"{mention} ❌ **Account unbind canceled.**"
                await interaction.response.edit_message(content=reply_text, view=None)

            confirm_btn.callback = button_callback
            cancel_btn.callback = button_callback

            if ctx.interaction:
                await ctx.interaction.response.send_message(
                    f"{mention} ⚠️ **Are you sure you want to unbind your account?**\n-# You have 10 seconds to respond.",
                    view=view,
                    ephemeral=True
                )
            else:
                await ctx.send(
                    f"{mention} ⚠️ **Are you sure you want to unbind your account?\n-# You have 10 seconds to respond.**",
                    view=view
                )

            await view.wait()

            if not result["done"]:
                timeout_msg = f"{mention} ⏰ **Timeout: no response received. Operation canceled.**"
                if ctx.interaction:
                    await ctx.interaction.followup.send(timeout_msg, ephemeral=True)
                else:
                    await ctx.send(timeout_msg)

        except Exception as e:
            error_msg = f"{mention} ❌ **An error occurred while processing your request.**"
            if ctx.interaction:
                await ctx.interaction.followup.send(error_msg, ephemeral=True)
            else:
                await ctx.send(error_msg)
            print("Error in unbind_account command:", e)