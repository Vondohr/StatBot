import discord
from discord import app_commands
from discord.ext import commands

class Companion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="companion", description="Show my Companion")
    async def companion(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(color=discord.Color.dark_purple())
        # embed.set_image(url="https://compote.slate.com/images/1aeebdcb-9972-40bf-b5f1-05f32888b59d.gif")
        
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
        buttons = [
            ("Feed", "green", "feed_companion", "\U0001F6DE"),
            ("Pet", "red", "pet_companion", "\U0001F479"),
            ("Teach", "grey", "teach_companion", "\U0001F3F4"),
            ("Train", "blurple", "train_companion", "\U0001F3B2")
            ("Use (Roll)", "blurple", "roll_companion", "\U0001F3B2")
            ("Rename", "blurple", "rename_companion", "\U0001F3B2")
        ]
        embed.set_image(url="https://static.wikia.nocookie.net/starwars/images/1/16/BD-1_JFO.png")
        embed.set_thumbnail(url="https://staticdelivery.nexusmods.com/mods/3061/images/thumbnails/800/800-1736279938-532506678.png")

        view = discord.ui.View()
        for label, style, custom_id, emoji in buttons:
            button = discord.ui.Button(label=label, style=getattr(discord.ButtonStyle, style), custom_id=custom_id, emoji=emoji)
            view.add_item(button)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Companion(bot))