import random
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
            description="Choose your drink by clicking one of the buttons below.\n\n**The Galaxy's Usuals**\n- **🍺 Skannbult Ale** - A cheap beverage, safe to drink.\n- **🥛 Bantha Milk** - A **small chance** to get a bonus or debuff to Rolls.\n- **🍸 Fuzzy Tauntaun** - A **big chance** to get a bonus or debuff to Rolls.\n- **🍷 Whyren’s Reserve** - A **small chance** to get a **BIG bonus** to Rolls, with a **BIG chance** to get a **BIG debuff** to Rolls.",
            color=discord.Color.blurple()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008654174552147/BarDefault.gif")

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
            title=f"**{interaction.user.display_name}** ordered the **🍺 Skannbult Ale!**",
            description="You enjoy this cheap beverage!",
            color=discord.Color.light_gray()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008655772713050/DrinkDefault.gif")
        embed.set_footer(text="It cost 50 ᖬ!")

        await interaction.response.send_message(embed=embed)

    # Button 2
    @discord.ui.button(label="🥛 Bantha Milk | 200 ᖬ", style=discord.ButtonStyle.blurple, custom_id="milk")
    async def milk(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "Player" not in [r.name for r in interaction.user.roles]:
            await interaction.response.send_message("You don't have a Character! Create one first.", ephemeral=True)
            return
        
        # TODO: implement action
        randomResult = random.randint(1, 10)

        if randomResult >= 1 and randomResult <= 2:
            embed = discord.Embed(
            title=f"**{interaction.user.display_name}** ordered the **🥛 Bantha Milk!**",
            description="You are **imbued** with energy after drinking this!\n\nYour Die will have 1 more side for your next Roll!",
            color=discord.Color.green()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008655193641031/DrinkSuccess.gif")
            embed.set_footer(text="It cost 200 ᖬ!")

        elif randomResult == 3:
            embed = discord.Embed(
            title=f"**{interaction.user.display_name}** ordered the **🥛 Bantha Milk!**",
            description="You don't feel so good after drinking it!\n\nYour Die will have 1 **fewer** sides for your next Roll!",
            color=discord.Color.red()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008654774472704/DrinkWrong.gif")
            embed.set_footer(text="It cost 200 ᖬ!")

        else:
            embed = discord.Embed(
            title=f"**{interaction.user.display_name}** ordered the **🥛 Bantha Milk!**",
            description="You enjoy this beverage!\n\nIt is very good, but doesn't give you any bonuses or debuffs.",
            color=discord.Color.light_gray()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008655772713050/DrinkDefault.gif")
            embed.set_footer(text="It cost 200 ᖬ!")

        await interaction.response.send_message(embed=embed)

    # Button 3
    @discord.ui.button(label="🍸 Fuzzy Tauntaun | 1 000 ᖬ", style=discord.ButtonStyle.green, custom_id="tauntaun")
    async def tauntaun(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "Player" not in [r.name for r in interaction.user.roles]:
            await interaction.response.send_message("You don't have a Character! Create one first.", ephemeral=True)
            return
        
        # TODO: implement action
        randomResult = random.randint(1, 10)

        if randomResult >= 1 and randomResult <= 3:
            embed = discord.Embed(
            title=f"**{interaction.user.display_name}** ordered the **🍸 Fuzzy Tauntaun!**",
            description="You are **imbued** with energy after drinking this!\n\nYour Die will have 2 more sides for your next Roll!",
            color=discord.Color.green()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008655193641031/DrinkSuccess.gif")
            embed.set_footer(text="It cost 1 000 ᖬ!")

        elif randomResult >= 4 and randomResult <= 6:
            embed = discord.Embed(
            title=f"**{interaction.user.display_name}** ordered the **🍸 Fuzzy Tauntaun!**",
            description="You don't feel so good after drinking it!\n\nYour Die will have 2 **fewer** sides for your next Roll!",
            color=discord.Color.red()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008654774472704/DrinkWrong.gif")
            embed.set_footer(text="It cost 1 000 ᖬ!")

        else:
            embed = discord.Embed(
            title=f"**{interaction.user.display_name}** ordered the **🍸 Fuzzy Tauntaun!**",
            description="You enjoy this expensive beverage!\n\nIt is very good, but doesn't give you any bonuses or debuffs.",
            color=discord.Color.light_gray()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008655772713050/DrinkDefault.gif")
            embed.set_footer(text="It cost 1 000 ᖬ!")

        await interaction.response.send_message(embed=embed)

    # Button 4
    @discord.ui.button(label="🍷 Whyren’s Reserve | 3 000 ᖬ", style=discord.ButtonStyle.red, custom_id="whyren")
    async def whyren(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "Player" not in [r.name for r in interaction.user.roles]:
            await interaction.response.send_message("You don't have a Character! Create one first.", ephemeral=True)
            return
        
        # TODO: implement action
        randomResult = random.randint(1, 10)
        
        if randomResult == 1:
            embed = discord.Embed(
            title=f"**{interaction.user.display_name}** ordered the **🍷 Whyren’s Reserve!**",
            description="You are **imbued** with energy after drinking this!\n\nYour Die will have 3 more sides for your next 2 Rolls!",
            color=discord.Color.green()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008655193641031/DrinkSuccess.gif")
            embed.set_footer(text="It cost 3 000 ᖬ!")

        elif randomResult >= 2 and randomResult <= 8:
            embed = discord.Embed(
            title=f"**{interaction.user.display_name}** ordered the **🍷 Whyren’s Reserve!**",
            description="You don't feel so good after drinking it!\n\nYour Die will have 3 **fewer** sides for your next 2 Rolls!",
            color=discord.Color.red()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008654774472704/DrinkWrong.gif")
            embed.set_footer(text="It cost 3 000 ᖬ!")

        else:
            embed = discord.Embed(
            title=f"**{interaction.user.display_name}** ordered the **🍷 Whyren’s Reserve!**",
            description="You enjoy this exclusive beverage!\n\nIt is very good, but doesn't give you any bonuses or debuffs.",
            color=discord.Color.light_gray()
            )
            embed.set_image(url="https://cdn.discordapp.com/attachments/1422602593179271189/1428008655772713050/DrinkDefault.gif")
            embed.set_footer(text="It cost 3 000 ᖬ!")

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(OrderDrinkCog(bot))