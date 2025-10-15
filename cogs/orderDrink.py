import sqlite3

import discord
from discord.ext import commands
from discord import app_commands

class OrderDrinkCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        '''
        iconn = sqlite3.connect("data/character_data/inventory.db")
        icur = iconn.cursor()
        icur.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                Id INTEGER PRIMARY KEY,
                Owner TEXT,
                Name TEXT,
                Description TEXT,
                BonusMin INTEGER,
                BonusMax INTEGER,
                Uses INTEGER,
                Amount INTEGER
            )
            """
        )
        iconn.commit()
        iconn.close()

        aconn = sqlite3.connect("data/character_data/activeBonuses.db")
        acur = aconn.cursor()
        acur.execute(
            """
            CREATE TABLE IF NOT EXISTS activeBonuses (
                Id INTEGER PRIMARY KEY,
                Owner TEXT,
                Name TEXT,
                Description TEXT,
                BonusMin INTEGER,
                BonusMax INTEGER,
                Uses INTEGER
            )
            """
        )
        aconn.commit()
        aconn.close()
        '''

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
        embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1427992029601857626/DrinkingObiWan.gif")

        view = DrinkButtons()
        await interaction.response.send_message(embed=embed, view=view)

class DrinkButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout so buttons always work

    # Button 1
    @discord.ui.button(label="🍺 Skannbult Ale | 50 ᖬ", style=discord.ButtonStyle.gray, custom_id="ale")
    async def ale(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "Player" not in [r.name for r in interaction.user.roles]:
            await interaction.response.send_message("You don't have a Character! Create one first.", ephemeral=True)
            return
        
        # TODO: Take away the credits

        embed = discord.Embed(
            title="🍺 Skannbult Ale",
            description="You enjoy this cheap beverage!",
            color=discord.Color.light_gray()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1427992029056467026/MilkDrinking.gif")
        embed.set_footer(text="It cost 50 ᖬ!")

        await interaction.response.send_message(embed=embed)

    # Button 2
    @discord.ui.button(label="🥛 Bantha Milk | 200 ᖬ", style=discord.ButtonStyle.blurple, custom_id="milk")
    async def milk(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "Player" not in [r.name for r in interaction.user.roles]:
            await interaction.response.send_message("You don't have a Character!", ephemeral=True)
            return
        
        # TODO: implement action
        await interaction.response.send_message("You clicked Drink 1!", ephemeral=True)

    # Button 3
    @discord.ui.button(label="🍸 Fuzzy Tauntaun | 1 000 ᖬ", style=discord.ButtonStyle.green, custom_id="tauntaun")
    async def tauntaun(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "Player" not in [r.name for r in interaction.user.roles]:
            await interaction.response.send_message("You don't have a Character!", ephemeral=True)
            return
        
        # TODO: implement action
        await interaction.response.send_message("You clicked Drink 2!", ephemeral=True)

    # Button 4
    @discord.ui.button(label="🍷 Whyren’s Reserve | 3 000 ᖬ", style=discord.ButtonStyle.red, custom_id="whyren")
    async def whyren(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "Player" not in [r.name for r in interaction.user.roles]:
            await interaction.response.send_message("You don't have a Character!", ephemeral=True)
            return
        
        # TODO: implement action
        await interaction.response.send_message("You clicked Drink 3!", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(OrderDrinkCog(bot))