import discord
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import asyncio

# =======================
# CONFIGURATION SECTION
# =======================

SUPPORTER_CHANNEL_ID = 1438517684470939829

# Role names exactly as they are on your server
ROLE_ULTRA = "Ultra Supporter"
ROLE_TOP = "Top Supporter"
ROLE_BOOSTER = "Server Booster"
ROLE_SUPPORTER = "Supporter"

# Embed images
ULTRA_IMAGE_URL = "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607000547480/UltraSupporter.gif"
TOP_IMAGE_URL = "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607398875246/TopSupporter.gif"
SUPPORTER_IMAGE_URL = "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607801794580/Supporter.gif"


class SupportersList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_update_loop.start()

    def cog_unload(self):
        self.daily_update_loop.cancel()

    # ---------------------------
    # Helper: Get all members for one or more roles
    # ---------------------------
    def get_members_with_role(self, members_list, role_names):
        role_names_set = set(role_names)
        matched = []
        for member in members_list:
            member_role_names = {r.name for r in member.roles}
            if member_role_names & role_names_set:
                matched.append(member)
        return sorted(matched, key=lambda m: m.name.lower())

    # ---------------------------
    # Helper: Create embed
    # ---------------------------
    def create_embed(self, title, members, image_url):
        if members:
            description = "\n".join(f"- {m.mention}" for m in members)
        else:
            description = "*No supporters in this tier yet.*"

        embed = discord.Embed(
            title=title,
            description=description,
            color=0x006FFF
        )
        embed.set_image(url=image_url)
        return embed

    # ---------------------------
    # Task: update all embeds once per day at noon
    # ---------------------------
    @tasks.loop(minutes=1)
    async def daily_update_loop(self):
        now = datetime.now()
        if now.time().hour == 12 and now.time().minute == 0:
            await self.update_supporter_embeds()

    async def update_supporter_embeds(self):
        await self.bot.wait_until_ready()
        guild = self.bot.guilds[0]
        channel = guild.get_channel(SUPPORTER_CHANNEL_ID)
        if channel is None:
            print("❌ Supporter channel not found!")
            return

        # Fetch all members to avoid cache issues
        try:
            members = [m async for m in guild.fetch_members(limit=None)]
        except Exception:
            members = list(guild.members)

        # Prepare member lists
        ultra_members = self.get_members_with_role(members, [ROLE_ULTRA])
        top_members = self.get_members_with_role(members, [ROLE_TOP, ROLE_BOOSTER])
        supporter_members = self.get_members_with_role(members, [ROLE_SUPPORTER])

        # Prepare embeds
        embeds_data = {
            "Ultra Supporters": self.create_embed("Ultra Supporters", ultra_members, ULTRA_IMAGE_URL),
            "Top Supporters (+ Server Boosters)": self.create_embed("Top Supporters (+ Server Boosters)", top_members, TOP_IMAGE_URL),
            "Supporters": self.create_embed("Supporters", supporter_members, SUPPORTER_IMAGE_URL),
        }

        # Fetch all messages in the channel
        try:
            messages = [m async for m in channel.history(limit=200)]
        except Exception as e:
            print("Error fetching messages:", e)
            return

        # Match embeds by title and edit them
        for title, embed in embeds_data.items():
            msg_to_edit = None
            for msg in messages:
                if msg.embeds and msg.embeds[0].title == title:
                    msg_to_edit = msg
                    break
            if msg_to_edit:
                try:
                    await msg_to_edit.edit(embed=embed)
                except Exception as e:
                    print(f"Failed to edit embed '{title}': {e}")
            else:
                # If embed with title doesn't exist, send it
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"Failed to send embed '{title}': {e}")


async def setup(bot):
    await bot.add_cog(SupportersList(bot))