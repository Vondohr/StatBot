# cogs/menu.py
import discord
from discord.ext import commands


class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Option 1", description="This is the first option", emoji=":assault:"
            ),
            discord.SelectOption(
                label="Option 2", description="This is the second option :assault:", emoji="😎"
            ),
            discord.SelectOption(
                label="Option 3", description="This is the third option", emoji="🔥"
            ),
        ]

        # Give a custom_id if you want this to be persistent across restarts
        super().__init__(
            placeholder="Choose an option...",
            min_values=1,
            max_values=1,
            options=options,
            # custom_id="menu:example:1",  # uncomment if using persistent views
        )

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]

        # Build a new embed based on the selection (or do whatever you need)
        new_embed = discord.Embed(
            title="You chose an option",
            description=f"**Selection:** {choice}",
            color=discord.Color.blurple(),
        )

        # Edit the original message so the dropdown stays visible
        await interaction.response.edit_message(embed=new_embed, view=self.view)


class DropdownView(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.add_item(Dropdown())


class MenuCog(commands.Cog):
    """Sends an embed with a dropdown (select) menu."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="menuTesting", description="Send an embed with a dropdown menu.")
    async def menu(self, ctx: commands.Context):
        """Works as both a prefix and slash command."""
        embed = discord.Embed(
            title="Choose an option",
            description="Use the dropdown below to make a selection.",
            color=discord.Color.green(),
        )
        view = DropdownView()
        # For slash invocations, use ctx.interaction.response first send; hybrid handles both:
        if hasattr(ctx, "interaction") and ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.interaction.response.send_message(embed=embed, view=view)
        else:
            await ctx.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    # If you want the view to be persistent across restarts:
    # bot.add_view(DropdownView(timeout=None))
    await bot.add_cog(MenuCog(bot))