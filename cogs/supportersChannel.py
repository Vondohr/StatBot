import discord
from discord.ext import commands
from discord import app_commands

class Supporters(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = 1438517684470939829  

        # Role groups configuration
        self.role_groups = {
            "Ultra Supporters": ["Ultra Supporter"],
            "Top Supporters & Boosters": ["Top Supporter", "Server Booster"],
            "Supporters": ["Supporter"],
        }

    async def cog_load(self):
        # Ensure embeds exist when the cog loads
        await self.bot.wait_until_ready()
        await self.ensure_embeds_exist()

    async def ensure_embeds_exist(self):
        """Create the supporter embeds if they don't exist yet."""
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"[Supporters] Channel {self.channel_id} not found or bot lacks permissions.")
            return

        # Fetch recent messages to see if embeds already exist
        try:
            messages = [m async for m in channel.history(limit=10)]
        except Exception as e:
            print(f"[Supporters] Could not read channel history: {e}")
            return

        found = {m.embeds[0].title: m for m in messages if m.embeds and m.embeds[0].title}

        # Ensure each embed exists
        for title in self.role_groups.keys():
            if title not in found:
                embed = discord.Embed(title=title, description="*(No supporters yet)*", color=discord.Color.blurple())
                await channel.send(embed=embed)

        # Update them immediately
        await self.update_all_embeds()

    async def update_all_embeds(self):
        """Update all supporter embeds with current members."""
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return

        # Fetch messages again to find the embeds
        try:
            messages = [m async for m in channel.history(limit=20)]
        except Exception as e:
            print(f"[Supporters] Could not read channel history: {e}")
            return

        embed_messages = {m.embeds[0].title: m for m in messages if m.embeds and m.embeds[0].title}

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

            if title in embed_messages:
                try:
                    await embed_messages[title].edit(embed=embed)
                except Exception as e:
                    print(f"[Supporters] Failed to edit embed '{title}': {e}")
            else:
                try:
                    await channel.send(embed=embed)
                except Exception as e:
                    print(f"[Supporters] Failed to send embed '{title}': {e}")

    # ---------- Events ----------
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Update embeds when supporter roles change."""
        before_roles = {r.name for r in before.roles}
        after_roles = {r.name for r in after.roles}
        changed = before_roles ^ after_roles

        relevant = {r for roles in self.role_groups.values() for r in roles}
        if any(r in relevant for r in changed):
            await self.update_all_embeds()

    # ---------- Slash command ----------
    @app_commands.command(name="refresh_supporters", description="Manually refresh the supporter embeds.")
    async def refresh_supporters(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.update_all_embeds()
        await interaction.followup.send("✅ Supporter embeds refreshed!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Supporters(bot))