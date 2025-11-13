import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class Supporters(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = 1438517684470939829
        self.data_file = "supporter_embeds.json"

        # === CONFIG ===
        self.embeds_config = {
            "Ultra Supporters": {
                "roles": ["Ultra Supporter"],
                "color": discord.Color.gold(),
                "image_url": "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607000547480/UltraSupporter.gif",
                "message_id": None,
            },
            "Top Supporters & Boosters": {
                "roles": ["Top Supporter", "Server Booster"],
                "color": discord.Color.blurple(),
                "image_url": "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607398875246/TopSupporter.gif",
                "message_id": None,
            },
            "Supporters": {
                "roles": ["Supporter"],
                "color": discord.Color.green(),
                "image_url": "https://cdn.discordapp.com/attachments/1422602094262882457/1434843607801794580/Supporter.gif",
                "message_id": None,
            },
        }

        self.load_message_ids()

    # ---------- JSON ----------
    def load_message_ids(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for title, saved_data in saved.items():
                    if title in self.embeds_config:
                        self.embeds_config[title]["message_id"] = saved_data.get("message_id")
            except Exception as e:
                print(f"[Supporters] Failed to load JSON: {e}")

    def save_message_ids(self):
        data = {t: {"message_id": d["message_id"]} for t, d in self.embeds_config.items()}
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[Supporters] Failed to save JSON: {e}")

    # ---------- STARTUP ----------
    async def cog_load(self):
        # Wait until bot caches guilds/channels and is ready
        await self.bot.wait_until_ready()
        await self.ensure_embeds_exist()

    async def ensure_embeds_exist(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"[Supporters] Channel {self.channel_id} not found or not cached. Check bot permissions and channel ID.")
            return

        # Safely fetch recent messages with embeds
        try:
            messages = [m async for m in channel.history(limit=10)]
        except Exception as e:
            print(f"[Supporters] Failed to read channel history: {e}")
            messages = []

        found_titles = {}
        for m in messages:
            if m.embeds and m.embeds[0].title:
                found_titles[m.embeds[0].title] = m

        updated = False

        for title, data in self.embeds_config.items():
            msg = None
            if data["message_id"]:
                try:
                    msg = await channel.fetch_message(data["message_id"])
                except discord.NotFound:
                    msg = None
                except discord.Forbidden as e:
                    print(f"[Supporters] Forbidden fetching message {data['message_id']}: {e}")
                    msg = None
                except discord.HTTPException as e:
                    print(f"[Supporters] HTTPException fetching message {data['message_id']}: {e}")
                    msg = None

            if not msg:
                if title in found_titles:
                    msg = found_titles[title]
                    data["message_id"] = msg.id
                    updated = True
                else:
                    embed = discord.Embed(
                        title=title,
                        description="*(No supporters yet)*",
                        color=data["color"],
                    )
                    if data.get("image_url"):
                        embed.set_image(url=data["image_url"])
                    try:
                        msg = await channel.send(embed=embed)
                        data["message_id"] = msg.id
                        updated = True
                    except discord.Forbidden as e:
                        print(f"[Supporters] Forbidden sending embed to channel {self.channel_id}: {e}")
                        continue
                    except discord.HTTPException as e:
                        print(f"[Supporters] HTTPException sending embed: {e}")
                        continue

        if updated:
            self.save_message_ids()

        await self.update_all_embeds()

    # ---------- UPDATE ----------
    async def update_all_embeds(self):
        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            return
        guild = channel.guild
        for title in self.embeds_config.keys():
            await self.update_embed_for_category(guild, title)

    async def update_embed_for_category(self, guild: discord.Guild, title: str):
        channel = self.bot.get_channel(self.channel_id)
        data = self.embeds_config[title]
        message_id = data["message_id"]
        if not message_id:
            return

        # Collect non-bot members from the configured roles
        members = set()
        for role_name in data["roles"]:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                # Note: role.members requires Intents.members enabled (portal + code)
                members.update([m for m in role.members if not m.bot])

        members_list = [f"- {m.mention}" for m in sorted(members, key=lambda x: x.name.lower())]
        members_text = "\n".join(members_list) if members_list else "*(No supporters yet)*"

        # Truncate to stay under 4096 chars
        if len(members_text) > 4000:
            members_text = members_text[:4000] + "\n*(List truncated)*"

        embed = discord.Embed(title=title, description=members_text, color=data["color"])
        if data.get("image_url"):
            embed.set_image(url=data["image_url"])

        try:
            msg = await channel.fetch_message(message_id)
            await msg.edit(embed=embed)
        except discord.NotFound:
            try:
                new_msg = await channel.send(embed=embed)
                data["message_id"] = new_msg.id
                self.save_message_ids()
            except discord.Forbidden as e:
                print(f"[Supporters] Forbidden sending replacement embed: {e}")
            except discord.HTTPException as e:
                print(f"[Supporters] HTTPException sending replacement embed: {e}")
        except discord.Forbidden as e:
            print(f"[Supporters] Forbidden editing message {message_id}: {e}")
        except discord.HTTPException as e:
            print(f"[Supporters] HTTPException editing message {message_id}: {e}")

    # ---------- EVENTS ----------
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # Requires Intents.members to fire
        before_roles = {r.name for r in before.roles}
        after_roles = {r.name for r in after.roles}
        changed = before_roles ^ after_roles
        relevant = {r for d in self.embeds_config.values() for r in d["roles"]}
        if any(r in relevant for r in changed):
            await self.update_all_embeds()

    # ---------- SLASH COMMAND ----------
    @app_commands.command(name="refresh_supporters", description="Manually refresh the supporter embeds.")
    @app_commands.default_permissions(manage_guild=True)  # controls visibility in the client
    @app_commands.checks.has_permissions(manage_guild=True)  # runtime gate (optional)
    async def refresh_supporters(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.update_all_embeds()
        await interaction.followup.send("✅ Supporter embeds refreshed!", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Supporters(bot))
