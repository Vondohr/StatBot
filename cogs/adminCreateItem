import discord
from discord.ext import commands
from discord import app_commands

class AdminItemCreate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="admin_item_create", description="Create a new item (admin only)")
    @app_commands.describe(name="Name of the new item")
    @app_commands.describe(description="Description of the new item")
    @app_commands.describe(amount="How many times should this item be added to your Inventory")
    async def admin_item_create(
        self,
        interaction: discord.Interaction,
        name: app_commands.Range[str, 1, 20],  # min 1, max 20 characters
        description: app_commands.Range[str, 1, 35],  # min 1, max 35 characters
        amount: app_commands.Range[int, 1, 10]  # only 1 to 10 allowed
    ):

        await interaction.response.send_message(
            f"✅ Created item:\n**Name**: `{name}`\n**Description**: `{description}`\n**Amount**: `{amount}`",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(AdminItemCreate(bot))