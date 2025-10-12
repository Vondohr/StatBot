import discord
from discord import app_commands
from discord.ext import commands

class TestModal(discord.ui.Modal, title="Test Modal"):
    answer = discord.ui.TextInput(label="Say something")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You said: {self.answer.value}", ephemeral=True)


class TestModalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="test_modal", description="Simple modal test")
    async def test_modal(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TestModal())


async def setup(bot: commands.Bot):
    await bot.add_cog(TestModalCog(bot))