import discord
from discord.ext import commands
from discord import app_commands

class TestCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="pingtest", description="Simple test command to check Cog registration.")
    async def pingtest(self, interaction: discord.Interaction):
        await interaction.response.send_message("🏓 Pong! The Cog is working.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TestCog(bot))