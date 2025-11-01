import json
import os
import asyncio
from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

# ReferralCog for discord.py (v2) — stores referral invites and awards bonuses using JSON persistence.
# Features:
# - /referral_create  -> creates a tracked invite for the user (only in specified category)
# - on_member_join -> detects used invite and credits inviter
# - /referral_my -> shows your referral count and referred users
# - /referral_leaderboard -> top referrers
# - /admin_referral_reset -> resets all referral data (restricted to Narrators role)
# - /admin_referral_forcegive -> admin-only manual credit
#
# Data saved in referrals.json in the working directory.

DATA_PATH = "referrals.json"
ALLOWED_CATEGORY_ID = 1259264566387413003  # Only this category allows referral creation


class ReferralCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._invites_cache: dict[int, dict[str, int]] = {}
        self._lock = asyncio.Lock()
        self.data = self._load_data()

    # ---------- JSON Persistence ----------

    def _load_data(self):
        if not os.path.exists(DATA_PATH):
            return {"invite_map": {}, "referrals": []}
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_data(self):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    # ---------- Invite Caching ----------

    async def _cache_guild_invites(self, guild: discord.Guild):
        try:
            invites = await guild.invites()
        except discord.Forbidden:
            return
        self._invites_cache[guild.id] = {i.code: i.uses for i in invites}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self._cache_guild_invites(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self._cache_guild_invites(guild)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        await self._cache_guild_invites(invite.guild)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        if guild.id not in self._invites_cache:
            await self._cache_guild_invites(guild)

        try:
            invites = await guild.invites()
        except discord.Forbidden:
            return

        used_code: Optional[str] = None
        async with self._lock:
            old = self._invites_cache.get(guild.id, {})
            new = {i.code: i.uses for i in invites}
            for code, uses in new.items():
                if uses > old.get(code, 0):
                    used_code = code
                    break
            self._invites_cache[guild.id] = new

        if not used_code:
            return

        inviter_id = self.data["invite_map"].get(used_code)
        if not inviter_id or inviter_id == member.id:
            return

        already = any(r["referred_id"] == member.id for r in self.data["referrals"])
        if not already:
            self.data["referrals"].append({
                "inviter_id": inviter_id,
                "referred_id": member.id,
                "timestamp": discord.utils.utcnow().timestamp(),
                "invite_code": used_code,
            })
            self._save_data()

    # ---------- Commands ----------

    @app_commands.command(name="referral_create", description="Create a tracked invite and register it to you")
    async def slash_create_invite(self, interaction: discord.Interaction):
        channel = interaction.channel

        if not isinstance(channel, discord.abc.GuildChannel):
            await interaction.response.send_message("This command must be used in a server channel.", ephemeral=True)
            return

        # Check if channel is inside the allowed category
        if not channel.category or channel.category.id != ALLOWED_CATEGORY_ID:
            await interaction.response.send_message(
                "You can only create referral invites in the designated referral category.",
                ephemeral=True
            )
            return

        try:
            invite = await channel.create_invite(max_age=0, max_uses=0, unique=True, reason=f"Referral invite by {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to create invites in this channel.", ephemeral=True)
            return

        self.data["invite_map"][invite.code] = interaction.user.id
        self._save_data()

        await interaction.response.send_message(f"Tracked invite created: {invite.url}", ephemeral=False)

    @app_commands.command(name="referral_my", description="Show your referral count and referred users")
    async def slash_my_referrals(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        my_refs = [r for r in self.data["referrals"] if r["inviter_id"] == user_id]
        count = len(my_refs)

        embed = discord.Embed(title="Your referrals", color=discord.Color.green())
        embed.add_field(name="Total successful referrals", value=str(count), inline=False)
        if my_refs:
            mentions = "\n".join(f"<@{r['referred_id']}>" for r in my_refs)
            embed.add_field(name="Referred members", value=mentions, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="referral_leaderboard", description="Show top referrers in this server")
    async def slash_leaderboard(self, interaction: discord.Interaction):
        counts = {}
        for r in self.data["referrals"]:
            counts[r["inviter_id"]] = counts.get(r["inviter_id"], 0) + 1
        sorted_refs = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:10]

        embed = discord.Embed(title="Referral leaderboard", color=discord.Color.blurple())
        if not sorted_refs:
            embed.description = "No referrals recorded yet."
        else:
            lines = [f"**{i+1}.** <@{uid}> — {cnt}" for i, (uid, cnt) in enumerate(sorted_refs)]
            embed.description = "\n".join(lines)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="admin_referral_reset", description="Reset all referral data (Narrators only)")
    async def slash_reset(self, interaction: discord.Interaction):
        if not any(role.name == "Narrators" for role in interaction.user.roles):
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        self.data = {"invite_map": {}, "referrals": []}
        self._save_data()
        await interaction.response.send_message("All referral data has been reset.", ephemeral=True)

    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.command(name="admin_referral_forcegive", description="Force-give a referral credit (admin only)")
    async def slash_force_give(self, interaction: discord.Interaction, inviter: discord.User, referred: discord.User):
        already = any(r["referred_id"] == referred.id for r in self.data["referrals"])
        if not already:
            self.data["referrals"].append({
                "inviter_id": inviter.id,
                "referred_id": referred.id,
                "timestamp": discord.utils.utcnow().timestamp(),
                "invite_code": None,
            })
            self._save_data()
        await interaction.response.send_message(f"Recorded referral: <@{inviter.id}> <- <@{referred.id}>")

async def setup(bot: commands.Bot):
    await bot.add_cog(ReferralCog(bot))