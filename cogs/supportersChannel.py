import discord
from discord.ext import commands
from discord import app_commands

class Supporters(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = 1260348000316817501  # replace with your channel ID

        # Role groups
        self.role_groups = {
            "Ultra Supporters": ["Ultra Supporter"],
            "Top Supporters & Boosters": ["Top Supporter", "Server Booster"],
            "Supporters": ["Supporter"],
        }

    async def cog_load(self):
        # Don’t let startup crash if embeds fail
        await self.bot.wait_until_ready()
        try:
            await self.update_all_embeds()
        except Exception as e:
            print(f"[Supporters] Startup embed update failed: {e}")

    async def update_all_embeds(self):
        """Update all supporter embeds with current members."""
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"[Supporters] Channel {self.channel_id} not found or bot lacks permissions.")
            return

        guild = channel.guild
        for title, roles in self.role_groups.items():
            members = set()
            for role_name in roles:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    members.update([m for m in role.members if not m.bot])

            description = "\n".join(f"- {m.mention}" for m in sorted(members, key=lambda x: x.name.lower()))
            if not description:
                description = "*(No supporters yet)*"

            embed = discord.Embed(title=title, description=description, color=discord.Color.blurple())

            # Try to find an existing message with this title
            try:
                messages = [m async for m in channel.history(limit=20)]
                target = next((m for m in messages if m.embeds and m.embeds[0].title == title), None)
                if target:
                    await target.edit(embed=embed)
                else:
                    await channel.send(embed=embed)
            except Exception as e:
                print(f"[Supporters] Failed to update/send embed '{title}': {e}")

    # ---------- Events ----------
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Update embeds when supporter roles change."""
        before_roles = {r.name for r in before.roles}
        after_roles = {r.name for r in after.roles}
        changed = before_roles ^ after_roles

        relevant = {r for roles in self.role_groups.values() for r in roles}
        if any(r in relevant for r in changed):
            try:
                await self.update_all_embeds()
            except Exception as e:
                print(f"[Supporters] Failed to update embeds on member update: {e}")

    # ---------- Slash command ----------
    @app_commands.command(name="refresh_supporters", description="Manually refresh the supporter embeds.")
    async def refresh_supporters(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            await self.update_all_embeds()
            await interaction.followup.send("✅ Supporter embeds refreshed!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Failed to refresh embeds: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Supporters(bot))
