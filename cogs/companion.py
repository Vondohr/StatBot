import random
import discord
from discord import app_commands
from discord.ext import commands

# Modal for renaming
class RenameModal(discord.ui.Modal, title="Rename Your Companion"):
    new_name = discord.ui.TextInput(label="New Name", placeholder="Enter a new name for your companion")

    async def on_submit(self, interaction: discord.Interaction):
        # This acts as the listener
        await interaction.response.send_message(
            f"✅ Your companion has been renamed to **{self.new_name.value}**!", ephemeral=True
        )


# Button View with listeners, restricted to one user
class CompanionView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user  # Store the user who invoked the command

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                "❌ These buttons aren't for you.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Feed", style=discord.ButtonStyle.green, custom_id="feed_companion", emoji="🥣")
    async def feed(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🍽️ You fed your companion!", ephemeral=True)

    @discord.ui.button(label="Pet", style=discord.ButtonStyle.green, custom_id="pet_companion", emoji="♥️")
    async def pet(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🐾 You gave your companion some pets!", ephemeral=True)

    @discord.ui.button(label="Teach", style=discord.ButtonStyle.blurple, custom_id="teach_companion", emoji="📖")
    async def teach(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📚 You taught your companion something new!", ephemeral=True)

    @discord.ui.button(label="Train", style=discord.ButtonStyle.blurple, custom_id="train_companion", emoji="🔁")
    async def train(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🏋️ Your companion has trained!", ephemeral=True)

    @discord.ui.button(label="Use (Roll)", style=discord.ButtonStyle.red, custom_id="roll_companion", emoji="🎲")
    async def roll(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🎲 You rolled with your companion!", ephemeral=True)

        roll = random.randint(1, 15)

        embed = discord.Embed(
            title=f"**{interaction.user.display_name}'s** companion rolled its die! 🎲",
            description=f"# ⟪ [{roll}](https://www.youtube.com/watch?v=dQw4w9WgXcQ) ⟫",
            color=discord.Color.dark_gray()
        )

        await interaction.channel.send(embed=embed)

    @discord.ui.button(label="Rename", style=discord.ButtonStyle.grey, custom_id="rename_companion", emoji="📝")
    async def rename(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RenameModal())


# The main command
class Companion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="companion", description="Show my Companion")
    @discord.app_commands.describe(hidden="Should the message be hidden")
    async def companion(self, interaction: discord.Interaction, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        embed = discord.Embed(color=discord.Color.dark_purple())
        embed.title = "Name of the Companion"
        embed.description = (
            "**Vitality:** 24/32\n"
            "**Species:** Axolotl\n\n"
            "**Abilities:**\n"
            "- Blabla\n"
            "- Blablabla\n\n"
            "**Level:** 10\n"
            "- Adds blabla to the Companion's Die"
        )
        embed.set_image(url="https://static.wikia.nocookie.net/starwars/images/1/16/BD-1_JFO.png")
        embed.set_thumbnail(url="https://staticdelivery.nexusmods.com/mods/3061/images/thumbnails/800/800-1736279938-532506678.png")

        view = CompanionView(user=interaction.user)
        await interaction.followup.send(embed=embed, view=view, ephemeral=hidden)


# Register the command and view
async def setup(bot):
    await bot.add_cog(Companion(bot))