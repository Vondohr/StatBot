import discord
from discord.ext import commands
from discord import app_commands
import os

FORUM_CATEGORY_ID = 1303296165923786782

# Predefined posts and corresponding GIF filenames
PREDEFINED_POSTS = {
    "Cockpit": "Cockpit.gif",
    "Common Room": "CommonRoom.gif",
    "Crew Quarters": "CrewQuarters.gif",
    "Engineering": "Engineering.gif",
    "Captain's Quarters": "CaptainsQuarters.gif",
    "Gunner Bay": "GunnerBay.gif",
    "OOC Lounge (Discussions & Planning)": "OOCLounge.gif"
}

class AdminCreateSpaceship(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_create_spaceship", description="Create a new spaceship forum with default rooms")
    @app_commands.describe(spaceship_name="Name of the new spaceship")
    async def admin_create_spaceship(self, interaction: discord.Interaction, spaceship_name: str):
        await interaction.response.defer(ephemeral=True)

        roles = [role.name for role in interaction.user.roles]
        if "Narrators" not in roles:
            await interaction.followup.send("You are not allowed to use this command!", ephemeral=True)
            return

        interaction.followup.send(f"Running discord.py version:", discord.__version__)

async def setup(bot):
    await bot.add_cog(AdminCreateSpaceship(bot))