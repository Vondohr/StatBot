# cogs/menu.py
import discord
from discord import app_commands
from discord.ext import commands


class Dropdown(discord.ui.Select):
    def __init__(self, assault_emoji: discord.Emoji | discord.PartialEmoji | None = None):
        options = [
            discord.SelectOption(
                label="Option 1",
                description="This is the first option",
                emoji=assault_emoji or "🛡️",  # fallback if not found
            ),
            discord.SelectOption(
                label="Option 2",
                description="This is the second option",
                emoji="😎",
            ),
            discord.SelectOption(
                label="Option 3",
                description="This is the third option",
                emoji="🔥",
            ),
        ]
        super().__init__(
            placeholder="Choose an option...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        new_embed = discord.Embed(
            title="You chose an option",
            description=f"**Selection:** {choice}",
            color=discord.Color.blurple(),
        )
        await interaction.response.edit_message(embed=new_embed, view=self.view)


class DropdownView(discord.ui.View):
    def __init__(self, assault_emoji: discord.Emoji | discord.PartialEmoji | None, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.add_item(Dropdown(assault_emoji))


class MenuCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="menurolldown", description="Show my companion")
    async def menurolldown(self, interaction: discord.Interaction):
        # Try to find the emoji in the CURRENT guild
        assault = discord.utils.get(interaction.guild.emojis, name="assault")

        # OPTIONAL: if the emoji lives in another guild, fetch it from there by ID
        # OTHER_GUILD_ID = 123456789012345678
        # assault = discord.utils.get(self.bot.get_guild(OTHER_GUILD_ID).emojis, name="assault")

        # If still not found but you know the ID:
        # assault = discord.PartialEmoji.from_str("<:assault:123456789012345678>")

        embed = discord.Embed(
            title="Choose an option",
            description="Use the dropdown below to make a selection.",
            color=discord.Color.green(),
        )
        view = DropdownView(assault_emoji=assault)
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(MenuCog(bot))