import asyncio
import discord
from discord import app_commands
from discord.ext import commands

@app_commands.command(name="test_modal")
async def test_modal(interaction: discord.Interaction):
    class TestModal(discord.ui.Modal, title="Test Modal"):
        answer = discord.ui.TextInput(label="Say something")

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.send_message(f"You said: {self.answer.value}")

    await interaction.response.send_modal(TestModal())
