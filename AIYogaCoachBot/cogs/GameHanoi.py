from discord.ext import commands
from discord.ui import Select, View
import discord

class HanoiGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="hanoitower", description="Play Hanoi Tower demo")
    async def game_hanoi(self, ctx):
        options = [
            discord.SelectOption(label=str(i), value=str(i), description=f"{i} disks")
            for i in range(1, 26)
        ]
        select = Select(placeholder="Select number of disks", options=options)

        async def select_callback(interaction: discord.Interaction):
            n = int(select.values[0])
            moves = []
            self.hanoi(n, "A", "C", "B", moves)
            if len(moves) > 40:
                display_moves = moves[:35] + ["... Too many steps, so they were omitted ..."] + moves[-5:]
            else:
                display_moves = moves

            move_text = "\n".join(display_moves)
            total_moves = len(moves)
            await interaction.response.send_message(
                f"**Hanoi Tower for {n} disks**\n\n{move_text}\n\nTotal moves: {total_moves}"
            )

        select.callback = select_callback

        view = View()
        view.add_item(select)

        await ctx.reply("Choose the number of disks for Hanoi Tower:", view=view, ephemeral=True)

    def hanoi(self, n, source, target, auxiliary, moves):
        if n == 1:
            moves.append(f"Move disk 1 from {source} to {target}")
        else:
            self.hanoi(n-1, source, auxiliary, target, moves)
            moves.append(f"Move disk {n} from {source} to {target}")
            self.hanoi(n-1, auxiliary, target, source, moves)