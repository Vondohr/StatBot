import discord
from discord import app_commands
from discord.ext import commands
import asyncio

THREAD_ID = 1422602094262882457
DEFAULT_IMAGE = "https://cdn.discordapp.com/attachments/1422602094262882457/1434843606660943872/Default.gif"
SUPPORTER_IMAGE = "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607801794580/Supporter.gif"
TOP_SUPPORTER_IMAGE = "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607398875246/TopSupporter.gif"
ULTRA_SUPPORTER_IMAGE = "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607000547480/UltraSupporter.gif"

class CharacterEmbedTesting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="character_embed_testing",
        description="Scans a forum thread for messages with a user ID."
    )
    @app_commands.describe(user_id="The numeric ID of the user to search for in the thread.")
    async def character_embed_testing(self, interaction: discord.Interaction, user_id: str):
        # Scans the defined forum thread for messages containing the given user ID

        await interaction.response.defer(thinking=True)

        thread = interaction.guild.get_thread(THREAD_ID)
        if thread is None:
            await interaction.followup.send("❌ The defined forum thread could not be found.")
            return

        supporterRoleID = 1291762245923241984
        topSupporterRoleID = 1291762480128725042
        ultraSupporterRoleID = 1291762664695005307
        serverBoosterRoleID = 1304150527306760212

        member = interaction.guild.get_member(user_id)
        stringToSearch = "Default"

        if interaction.guild.get_role(supporterRoleID) in member.roles:
            stringToSearch = "Supporter"
        elif interaction.guild.get_role(topSupporterRoleID) in member.roles:
            stringToSearch = "TopSupporter"
        elif interaction.guild.get_role(serverBoosterRoleID) in member.roles:
            stringToSearch = "TopSupporter"
        elif interaction.guild.get_role(ultraSupporterRoleID) in member.roles:
            stringToSearch = "UltraSupporter"
        else:
            stringToSearch = "Default"

        userIDFound = False
        imageURL = "Empty"

        async for message in thread.history(limit=200, oldest_first=True):
            # Check message content for user ID
            if user_id in message.content:
                userIDFound = True
                for attachment in message.attachments:
                    if attachment.url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                        if f"_{stringToSearch.lower}" in attachment.url.lower():
                            imageURL = attachment.url
                        else:
                            imageURL = "Empty"

        if not userIDFound:
            if stringToSearch == "Supporter":
                imageURL = SUPPORTER_IMAGE
            elif stringToSearch == "TopSupporter":
                imageURL = TOP_SUPPORTER_IMAGE
            elif stringToSearch == "UltraSupporter":
                imageURL = ULTRA_SUPPORTER_IMAGE
            else:
                imageURL = DEFAULT_IMAGE

        embed = discord.Embed(
            title="Testing Character Image",
            color=discord.Color.blue()
        )
        embed.set_image(url=imageURL)
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CharacterEmbedTesting(bot))