import discord
from discord import app_commands
from discord.ext import commands

class CategoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Dynamic choices generator for category names
    async def category_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        # Get all category channels in the guild
        categories = [
            c for c in interaction.guild.categories
            if current.lower() in c.name.lower()
        ]
        # Return up to 25 choices (Discord limit)
        return [
            app_commands.Choice(name=cat.name, value=str(cat.id))
            for cat in categories[:25]
        ]

    # Slash command that takes a category as input
    @app_commands.command(name="pick_category", description="Select a server category to track")
    @app_commands.describe(category="Pick a category")
    @app_commands.autocomplete(category=category_autocomplete)
    async def pick_category(self, interaction: discord.Interaction, category: str):
        category_obj = discord.utils.get(interaction.guild.categories, id=int(category))
        if category_obj:
            await interaction.response.send_message(f"You are now tracking the **{category_obj.name}** category", ephemeral=True)
            with open(f"{interaction.guild.id}.txt", "a", encoding="utf-8") as f:
                f.write(f"{category_obj.id}\n")
        else:
            await interaction.response.send_message("Category not found.", ephemeral=True)

    # Slash command that takes a category as input
    @app_commands.command(name="create_dashboard", description="Create a new dashboard for your categories to track")
    @app_commands.describe(dashboard="Name your dashboard")
    async def create_dashboard(self, interaction: discord.Interaction, dashboard: app_commands.Range[str, 1, 50]):
        with open(f"{interaction.guild.id}.txt", "a", encoding="utf-8") as f:
            f.write(f"{dashboard}\n")
        await interaction.response.send_message(f"Dashboard **{dashboard}** created")

# Load the cog
async def setup(bot):
    await bot.add_cog(CategoryCommands(bot))