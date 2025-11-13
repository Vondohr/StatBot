import discord
from discord.ext import commands, tasks

# =======================
# CONFIGURATION SECTION
# =======================

SUPPORTER_CHANNEL_ID = 1438517684470939829

# Role names exactly as they are on your server
ROLE_ULTRA = "Ultra Supporter"
ROLE_TOP = "Top Supporter"
ROLE_BOOSTER = "Server Booster"
ROLE_SUPPORTER = "Supporter"

# Embed images (PUT YOUR URLs HERE)
ULTRA_IMAGE_URL = "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607000547480/UltraSupporter.gif"
TOP_IMAGE_URL = "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607398875246/TopSupporter.gif"
SUPPORTER_IMAGE_URL = "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607801794580/Supporter.gif"


class SupportersList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Store sent embed message IDs (in-memory)
        self.message_ids = {
            "ultra": None,
            "top": None,
            "supporter": None
        }

        self.update_supporter_lists.start()

    def cog_unload(self):
        self.update_supporter_lists.cancel()

    # ---------------------------
    # Helper: Get all members for one or more roles
    # This version checks an explicit members list (fetched from API)
    # ---------------------------
    def get_members_with_role(self, members_list, role_names):
        role_names_set = set(role_names)
        matched = []

        for member in members_list:
            # Compare role names (safer than role objects when caching is weird)
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
    # Background update loop (runs every 20 seconds)
    # ---------------------------
    @tasks.loop(seconds=20)
    async def update_supporter_lists(self):
        await self.bot.wait_for("ready")

        if not self.bot.guilds:
            return

        guild = self.bot.guilds[0]
        channel = guild.get_channel(SUPPORTER_CHANNEL_ID)
        if channel is None:
            print("❌ Supporter channel not found!")
            return

        # ---------- CRITICAL CHANGE ----------
        # Fetch the full, current member list from the API to avoid stale cache issues.
        # This ensures manual role edits are reflected reliably.
        try:
            members = [m async for m in guild.fetch_members(limit=None)]
        except Exception:
            # Fallback to cached members if fetch fails for any reason
            members = list(guild.members)

        # Collect role-based member lists (using the fetched members)
        ultra_members = self.get_members_with_role(members, [ROLE_ULTRA])
        top_members = self.get_members_with_role(members, [ROLE_TOP, ROLE_BOOSTER])
        supporter_members = self.get_members_with_role(members, [ROLE_SUPPORTER])

        # Prepare embeds
        embeds = {
            "ultra": self.create_embed("Ultra Supporters", ultra_members, ULTRA_IMAGE_URL),
            "top": self.create_embed("Top Supporters (+ Server Boosters)", top_members, TOP_IMAGE_URL),
            "supporter": self.create_embed("Supporters", supporter_members, SUPPORTER_IMAGE_URL),
        }

        # Update or recreate messages
        for key, embed in embeds.items():
            msg_id = self.message_ids[key]

            if msg_id is None:
                # First-time creation
                msg = await channel.send(embed=embed)
                self.message_ids[key] = msg.id
                continue

            # Try editing
            try:
                msg = await channel.fetch_message(msg_id)
                await msg.edit(embed=embed)
            except discord.NotFound:
                # If deleted, recreate
                msg = await channel.send(embed=embed)
                self.message_ids[key] = msg.id

    # ---------------------------
    # Listeners: trigger auto-refresh
    # ---------------------------
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Compare role names sets to detect role changes
        before_set = {r.name for r in before.roles}
        after_set = {r.name for r in after.roles}

        tracked = {ROLE_ULTRA, ROLE_TOP, ROLE_BOOSTER, ROLE_SUPPORTER}

        if tracked & (before_set ^ after_set):
            # immediate refresh (the background loop will do the heavy lifting)
            self.update_supporter_lists.restart()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.update_supporter_lists.restart()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.update_supporter_lists.restart()


async def setup(bot):
    await bot.add_cog(SupportersList(bot))