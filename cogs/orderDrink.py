import discord
from discord.ext import commands
from discord import app_commands

class OrderDrinkCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Slash command
    @app_commands.command(name="order_drink", description="Order a drink")
    async def order_drink(self, interaction: discord.Interaction):
        if not "🧉" in interaction.channel.name:
            await interaction.response.send_message("You cannot order a drink outside Cantinas!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🍹 Order a Drink",
            description="Choose your drink by clicking one of the buttons below.",
            color=discord.Color.blurple()
        )

        view = DrinkButtons()
        await interaction.response.send_message(embed=embed, view=view)

class DrinkButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout so buttons always work

    # Button 1
    @discord.ui.button(label="🥛 Bantha Milk | 2 ᖬ", style=discord.ButtonStyle.blurple, custom_id="drink_1")
    async def drink_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: implement action
        await interaction.response.send_message("You clicked Drink 1!", ephemeral=True)

    # Button 2
    @discord.ui.button(label="🍸 Fuzzy Tauntaun | 5 ᖬ", style=discord.ButtonStyle.gray, custom_id="drink_2")
    async def drink_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: implement action
        await interaction.response.send_message("You clicked Drink 2!", ephemeral=True)

    # Button 3
    @discord.ui.button(label="🍷 Whyren’s Reserve | 10 ᖬ", style=discord.ButtonStyle.red, custom_id="drink_3")
    async def drink_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: implement action
        await interaction.response.send_message("You clicked Drink 3!", ephemeral=True)

    # Button 4
    @discord.ui.button(label="🍺 Skannbult Ale | 15 ᖬ", style=discord.ButtonStyle.green, custom_id="drink_4")
    async def drink_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: implement action
        await interaction.response.send_message("You clicked Drink 4!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(OrderDrinkCog(bot))