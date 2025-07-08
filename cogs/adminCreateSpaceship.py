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

        '''
        # Fetch the category
        category = interaction.guild.get_channel(FORUM_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.followup.send("Error: Category ID is invalid.", ephemeral=True)
            return

        # Create a new Forum channel
        try:
            forum = await interaction.guild.create_text_channel(
                name=spaceship_name,
                category=category,
                type=discord.ChannelType.forum,
                reason=f"Created by {interaction.user} via /admin_create_spaceship"
            )
        except Exception as e:
            await interaction.followup.send(f"Failed to create forum: {e}", ephemeral=True)
            return

        # Create each predefined post
        for post_name, gif_filename in PREDEFINED_POSTS.items():
            file_path = os.path.join(os.path.dirname(__file__), gif_filename)
            if not os.path.isfile(file_path):
                await interaction.followup.send(f"Missing file: {gif_filename}", ephemeral=True)
                continue

            try:
                with open(file_path, "rb") as f:
                    gif_file = discord.File(f, filename=gif_filename)
                    await forum.create_thread(
                        name=post_name,
                        content=f"**{post_name}** of the ship **{spaceship_name}**.",
                        file=gif_file
                    )
            except Exception as e:
                await interaction.followup.send(f"Failed to create post '{post_name}': {e}", ephemeral=True)

        await interaction.followup.send(f"Spaceship **{spaceship_name}** created with default rooms!", ephemeral=True)
        '''

async def setup(bot):
    await bot.add_cog(AdminCreateSpaceship(bot))