import discord
from discord.ext import commands
from discord import app_commands

class HelloCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="send_hello", description="Sends a hello message.")
    async def send_hello(self, interaction: discord.Interaction):
        await interaction.response.send_message("Hello")

async def setup(bot):
    await bot.add_cog(HelloCog(bot))