# cogs/menu.py
import discord
from discord import app_commands
from discord.ext import commands


class Dropdown(discord.ui.Select):
    def __init__(self, interaction: discord.Interaction):
        e = discord.utils.get(interaction.guild.emojis, name="assault")
        emojiAssault = discord.PartialEmoji.from_str(f"<:assault:{e.id}>")
        
        options = [
            discord.SelectOption(
                label="Option 1",
                description="This is the first option",
                # Use a Unicode emoji or a real custom emoji object (see note below).
                emoji=emojiAssault,
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
            # custom_id="menu:example:1",  # uncomment for persistent views
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
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.add_item(Dropdown())


class MenuCog(commands.Cog):
    """Sends an embed with a dropdown (select) menu."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="menurolldown", description="Show my companion")
    async def menurolldown(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Choose an option",
            description="Use the dropdown below to make a selection.",
            color=discord.Color.green(),
        )
        view = DropdownView()
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(MenuCog(bot))